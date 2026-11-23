"""Exact (z3) minimum of max_meet under lane-pair balance, for small cases.

    python3 exact.py M,K,B [...] [--timeout 120]

Model: x[a][b] = pair of bowler a in block b (one-hot), K bowlers per pair
per block, each bowler on each pair floor..ceil(B/M) blocks, block 1 fixed
(symmetry).  For cap = 1, 2, ... asks whether every couple can share a pair
in at most cap blocks.  Prints the least feasible cap and whether smaller caps
were proven infeasible (unsat) or timed out (unknown).  Results go to
results/exact.json and are quoted in the README as lower bounds.
"""
from __future__ import annotations

import json
import os
import sys

import z3

HERE = os.path.dirname(os.path.abspath(__file__))


def feasible(M, K, B, cap, timeout, want_draw=False):
    n = M * K
    pf, pc = B // M, -(-B // M)
    s = z3.Solver()
    s.set("timeout", timeout * 1000)
    x = [[[z3.Bool(f"x{a}_{b}_{p}") for p in range(M)] for b in range(B)] for a in range(n)]
    for a in range(n):
        for b in range(B):
            s.add(z3.PbEq([(x[a][b][p], 1) for p in range(M)], 1))
        for p in range(M):
            t = [(x[a][b][p], 1) for b in range(B)]
            s.add(z3.PbLe(t, pc))
            if pf:
                s.add(z3.PbGe(t, pf))
    for b in range(B):
        for p in range(M):
            s.add(z3.PbEq([(x[a][b][p], 1) for a in range(n)], K))
    for a in range(n):
        for p in range(M):
            s.add(x[a][0][p] if a // K == p else z3.Not(x[a][0][p]))
    for a in range(n):
        for c in range(a + 1, n):
            same = [z3.And(x[a][b][p], x[c][b][p]) for b in range(B) for p in range(M)]
            s.add(z3.PbLe([(v, 1) for v in same], cap))
    r = s.check()
    if not want_draw:
        return r
    if r != z3.sat:
        return r, None
    m = s.model()
    draw = [[[a for a in range(n) if z3.is_true(m.evaluate(x[a][b][p]))] for p in range(M)]
            for b in range(B)]
    return r, draw


def job(c, timeout, secs=8):
    """Least feasible cap for one case; the sat draw is polished by the anneal
    (bowling orders) and stored in results/opt/ if it beats what is there."""
    from optimum import run_case
    M, K, B = c
    log, draw = [], None
    for cap in range(1, B + 1):
        r, d = feasible(M, K, B, cap, timeout, want_draw=True)
        log.append((cap, str(r)))
        if r == z3.sat:
            draw = d
            break
    status = None
    if draw is not None:
        new = run_case(M, K, B, secs, 13, cap, draw)
        p = os.path.join(HERE, "results", "opt", f"M{M}_K{K}_B{B}.json")
        old = json.load(open(p)) if os.path.exists(p) else None
        if old is None or tuple(new["score"]) < tuple(old["score"]):
            json.dump(new, open(p, "w"))
            status = "improved"
    return c, log, status


def main():
    from concurrent.futures import ProcessPoolExecutor
    args = [x for x in sys.argv[1:] if "," in x]
    timeout = int(sys.argv[sys.argv.index("--timeout") + 1]) if "--timeout" in sys.argv else 120
    jobs = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 8
    cases = [tuple(map(int, c.split(","))) for c in args]
    path = os.environ.get("EXACT_OUT") or os.path.join(HERE, "results", "exact.json")
    res = json.load(open(path)) if os.path.exists(path) else {}
    with ProcessPoolExecutor(jobs) as ex:
        for (M, K, B), log, st in ex.map(job, cases, [timeout] * len(cases)):
            res[f"M{M}_K{K}_B{B}"] = log
            print(M, K, B, log, st or "", flush=True)
            json.dump(res, open(path, "w"), indent=0)


if __name__ == "__main__":
    main()
