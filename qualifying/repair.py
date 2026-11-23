"""Make an unconstrained draw lane-pair balanced by re-assigning its groups to
pairs (z3), keeping every group (so meetings are unchanged), then re-run the
anneal from it to fix bowling orders.

    python3 repair.py [--jobs 8] [--secs 10]

For each (M,K,B) with a draw in results/opt_free/, solve: in every block put
the M groups on the M pairs (a bijection) so that every bowler visits every
pair floor(B/M)..ceil(B/M) times.  If that is satisfiable the repaired draw is
annealed (phase 1 starts at its lower bound or improves it; phase 2 orders
the bowlers) and kept in results/opt/ if better.
"""
from __future__ import annotations

import argparse
import json
import os
from concurrent.futures import ProcessPoolExecutor

import z3

from optimum import HERE, run_case
from model import evaluate


def balance(draw, timeout_ms=60000):
    B, M, K = len(draw), len(draw[0]), len(draw[0][0])
    pf, pc = B // M, -(-B // M)
    s = z3.Solver()
    s.set("timeout", timeout_ms)
    y = [[[z3.Bool(f"y{b}_{g}_{p}") for p in range(M)] for g in range(M)] for b in range(B)]
    for b in range(B):
        for g in range(M):
            s.add(z3.PbEq([(y[b][g][p], 1) for p in range(M)], 1))
        for p in range(M):
            s.add(z3.PbEq([(y[b][g][p], 1) for g in range(M)], 1))
    for g in range(M):            # block 1 keeps its order (relabelling symmetry)
        s.add(y[0][g][g])
    where = {}
    for b in range(B):
        for g, grp in enumerate(draw[b]):
            for a in grp:
                where[(a, b)] = g
    n = M * K
    for a in range(n):
        for p in range(M):
            terms = [(y[b][where[(a, b)]][p], 1) for b in range(B)]
            s.add(z3.PbLe(terms, pc))
            if pf > 0:
                s.add(z3.PbGe(terms, pf))
    r = s.check()
    if r != z3.sat:
        return None, str(r)
    m = s.model()
    out = []
    for b in range(B):
        blk = [None] * M
        for g in range(M):
            for p in range(M):
                if z3.is_true(m.evaluate(y[b][g][p])):
                    blk[p] = draw[b][g]
        out.append(blk)
    return out, "sat"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--secs", type=float, default=10)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    cases = [tuple(map(int, s.split(","))) for s in a.only] if a.only else \
        [(M, K, B) for K in (2, 3, 4, 5) for M in range(3, 11) for B in range(2, 13)]

    with ProcessPoolExecutor(a.jobs) as ex:
        for c, st, sc in ex.map(job, cases, [a.secs] * len(cases)):
            print(*c, st, sc, flush=True)


def job(c, secs):
        M, K, B = c
        pfree = os.path.join(HERE, "results", "opt_free", f"M{M}_K{K}_B{B}.json")
        pcur = os.path.join(HERE, "results", "opt", f"M{M}_K{K}_B{B}.json")
        if not os.path.exists(pfree):
            return c, "nofree", None
        free = json.load(open(pfree))["draw"]
        cur = json.load(open(pcur)) if os.path.exists(pcur) else None
        fsc = tuple(evaluate(free)["score"][1:8])
        if cur and tuple(cur["score"][1:8]) <= fsc and cur["score"][0] == 0 + (B % M != 0):
            return c, "skip", cur["score"]
        bal, st = balance(free)
        if bal is None:
            return c, "unbalanceable:" + st, None
        new = run_case(M, K, B, secs, 7, None, bal)
        if cur is None or tuple(new["score"]) < tuple(cur["score"]):
            json.dump(new, open(pcur, "w"))
            return c, "improved", new["score"]
        return c, "kept", cur["score"]


if __name__ == "__main__":
    main()
