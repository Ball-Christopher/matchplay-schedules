"""Unrestricted (non-rule) designs: lower bounds + simulated annealing.

    python3 optimum.py [--secs 40] [--jobs 16] [--only M,K,B ...]

For each (M, K, B) computes a lower bound for every score field, runs
./anneal with targets set to those bounds, re-scores the result with
model.evaluate and writes results/opt/M{M}_K{K}_B{B}.json.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from math import comb

from model import SCORE_FIELDS, evaluate

HERE = os.path.dirname(os.path.abspath(__file__))

# Social golfer problem, M groups of K: (best known rounds, proven maximum).
# Source: Miller, Valkov & Abel, arXiv:2507.23376, Tables B4-B7 (r, MAX);
# K=2 is a round robin (1-factorisation); M < K allows only one round.
SGP = {}
for M in range(3, 11):
    SGP[(M, 2)] = (2 * M - 1, 2 * M - 1)
for M, r in zip(range(3, 11), (4, 4, 7, 8, 10, 11, 13, 14)):
    SGP[(M, 3)] = (r, r)
for M, r in zip(range(3, 11), (1, 5, 5, 7, 9, 10, 11, 13)):
    SGP[(M, 4)] = (r, r)
for M, r, mx in zip(range(3, 11), (1, 1, 6, 6, 7, 8, 9, 9), (1, 1, 6, 7, 8, 9, 11, 12)):
    SGP[(M, 5)] = (r, mx)


def bounds(M, K, B):
    """Lower bound for each field of model.SCORE_FIELDS (smaller is better).
    Uses the *proven* SGP maximum, so for open SGP cases the max_meet bound
    is 1 even though no such design is known."""
    n = M * K
    per = (K - 1) * B
    known, proven = SGP[(M, K)]
    mm = max(1, -(-per // (n - 1)))
    if B > proven:
        mm = max(mm, 2)
    rep = (n * max(0, per - (n - 1)) + 1) // 2
    if B > proven:
        rep = max(rep, 1)
    minm = per // (n - 1)
    if K == 2:
        T = M * B
        mf, frep, mu, urep = mm, 2 * rep, 2 * mm, T + rep
    else:
        mf = max(1, -(-B // (n - 1)))
        frep = max(0, n * B - n * (n - 1))
        mu = max(1, -(-(n * B) // comb(n, 2)))
        urep = max(0, n * B - comb(n, 2))
    ps = 0 if B % M == 0 else 1
    ss = 0 if (M * B * ((K + 1) // 2)) % n == 0 else 1
    qs = 0 if B % K == 0 else 1
    lb = dict(pair_spread=ps, max_meet=mm, max_follow=mf, repeats=rep, follow_repeats=frep,
              max_ufollow=mu, ufollow_repeats=urep, neg_min_meet=-minm,
              side_spread=ss, pos_spread=qs)
    return lb, known


def status(score, lb):
    """Number of leading fields proven optimal (score == lower bound)."""
    k = 0
    for f, v in zip(SCORE_FIELDS, score):
        if v != lb[f]:
            break
        k += 1
    return k


def rule_best(M, K, B):
    """Best rule for (M,K,B) from results/rules (rulesearch output)."""
    path = os.path.join(HERE, "results", "rules", f"M{M}_K{K}.jsonl")
    for line in open(path):
        r = json.loads(line)
        if r["kind"] == "best" and r["B"] == B:
            return r
    return None


def run_case(M, K, B, secs, seed=1, capM=None, init=None):
    lb, known = bounds(M, K, B)
    if capM is None:
        capM = lb["max_meet"] if B <= known or lb["max_meet"] > 1 else 2
    capU = lb["max_ufollow"] if K > 2 else 2 * capM
    capF = lb["max_follow"] if K > 2 else capM
    tmin = -lb["neg_min_meet"]
    lbc1 = lb["repeats"]
    lbc2 = 200 * lb["follow_repeats"] + 20 * lb["ufollow_repeats"]
    cmd = [os.path.join(HERE, "anneal"), str(M), str(K), str(B), str(secs), str(seed),
           str(capM), str(capF), str(capU), str(tmin), str(lbc1), str(lbc2)]
    if init is not None:
        # start from an explicit draw relabelled so block 1 is the identity
        first = [x for pr in init[0] for x in pr]
        rel = {a: i for i, a in enumerate(first)}
        path = os.path.join(HERE, "results", "opt", f"init_{M}_{K}_{B}_{seed}_{os.getpid()}_{id(init)}.txt")
        with open(path, "w") as f:
            for blk in init:
                f.write(" ".join(str(rel[x]) for pr in blk for x in pr) + "\n")
        cmd.append(path)
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    res = json.loads(out)
    if init is not None:
        os.remove(path)
    r = evaluate(res["draw"])
    return dict(M=M, K=K, B=B, score=list(r["score"]), lb=[lb[f] for f in SCORE_FIELDS],
                proven_fields=status(r["score"], lb), sgp_known=known,
                sgp_max=SGP[(M, K)][1], cost=[res["cost1"], res["cost2"]],
                metrics={k: v for k, v in r.items() if k != "score"},
                draw=res["draw"])


def better(a, b):
    return b is None or tuple(a["score"]) < tuple(b["score"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--secs", type=float, default=40)
    ap.add_argument("--jobs", type=int, default=16)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--capM", type=int)
    ap.add_argument("--construct", action="store_true",
                    help="start from the GF(q) transversal design (constructions.py) when it has >= B rounds")
    ap.add_argument("--soft", action="store_true",
                    help="random start, lane-pair balance as a soft penalty (ANNEAL_PW, default 4); "
                         "only cases not yet proven optimal")
    ap.add_argument("--maxB", type=int, default=12)
    ap.add_argument("--from-free", action="store_true",
                    help="start from the unconstrained draw in results/opt_free with balance as a "
                         "soft penalty (ANNEAL_PW, default 4); only cases not yet proven optimal")
    ap.add_argument("--from-rule", action="store_true",
                    help="start the anneal from the best movement rule's draw")
    a = ap.parse_args()
    os.makedirs(os.path.join(HERE, "results", "opt"), exist_ok=True)
    if a.only:
        cases = [tuple(map(int, s.split(","))) for s in a.only]
    else:
        cases = [(M, K, B) for K in (2, 3, 4, 5) for M in range(3, 11) for B in range(1, 13)]

    def job(c):
        M, K, B = c
        path = os.path.join(HERE, "results", "opt", f"M{M}_K{K}_B{B}.json")
        old = json.load(open(path)) if os.path.exists(path) else None
        if old and old["proven_fields"] == len(SCORE_FIELDS):
            return c, old, False
        init = None
        if a.from_rule:
            from model import rule_draw
            rb = rule_best(M, K, B)
            init = rule_draw(M, K, B, rb["d"], rb["pi"])
        if B > a.maxB:
            return c, old, False
        if a.soft:
            if old and old["proven_fields"] >= 8:
                return c, old, False
            os.environ["ANNEAL_SOFT"] = "1"
            os.environ.setdefault("ANNEAL_PW", "4")
            os.environ.setdefault("ANNEAL_T", "1")
        if a.from_free:
            pf_ = os.path.join(HERE, "results", "opt_free", f"M{M}_K{K}_B{B}.json")
            if not os.path.exists(pf_) or (old and old["proven_fields"] >= 8):
                return c, old, False
            init = json.load(open(pf_))["draw"]
            os.environ.setdefault("ANNEAL_PW", "4")
            os.environ.setdefault("ANNEAL_T", "1")
        if a.construct:
            from constructions import field_design
            fd = field_design(M, K)
            if not fd or len(fd) < B:
                return c, old, False
            init = fd[:B]
        new = run_case(M, K, B, a.secs, a.seed, a.capM, init)
        if better(new, old):
            json.dump(new, open(path, "w"))
            return c, new, True
        return c, old, False

    with ThreadPoolExecutor(a.jobs) as ex:
        for (M, K, B), r, upd in ex.map(job, cases):
            print(M, K, B, r["score"], "lb", r["lb"], "proven", r["proven_fields"],
                  "updated" if upd else "", flush=True)


if __name__ == "__main__":
    main()
