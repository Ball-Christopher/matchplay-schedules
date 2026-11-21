#!/usr/bin/env python3
"""z3 search (optionally with exact lane balance built in, LANES=1) for a resolvable 2-(v,3,2) design (v = 0 mod 6) with a good prefix
profile: weeks 1..K pair-disjoint and every couple met by week C.  Then the only
prefixes with spread 2 are K+1..C-1.  Lower bound: C-K >= 2 (see gen.py note).

Usage: python3 prefix_sat.py v K C timeout_seconds [lam] [lanes]
  -> writes design_v{v}_sat.json (weeks as lists of groups, group g = lane pair g
     when lanes=1).  For lam=1 use K=C=r (no prefix constraint needed).
"""
import json
import sys
import time
from itertools import combinations
from pathlib import Path

import z3

v, K, C, T = (int(x) for x in sys.argv[1:5])
lam = int(sys.argv[5]) if len(sys.argv) > 5 else 2
lanes = len(sys.argv) > 6 and sys.argv[6] == "1"
r, ng = lam * (v - 1) // 2, v // 3
P = range(v)
x = [[[z3.Bool(f"x{w}_{p}_{g}") for g in range(ng)] for p in P] for w in range(r)]
s = z3.SolverFor("QF_FD")
s.set("timeout", T * 1000)
for w in range(r):
    for p in P:
        s.add(z3.PbEq([(x[w][p][g], 1) for g in range(ng)], 1))
    for g in range(ng):
        s.add(z3.PbEq([(x[w][p][g], 1) for p in P], 3))
    if lanes:
        continue
    # symmetry: groups numbered by their smallest member
    s.add(x[w][0][0])
    for g in range(1, ng):
        # smallest member of group g is larger than smallest of group g-1
        for p in P:
            s.add(z3.Implies(x[w][p][g], z3.Or([x[w][q][g - 1] for q in range(p)] or [False])))
# week 1 fixed
for p in P:
    s.add(x[0][p][p // 3])
m = {}
for a, b in combinations(P, 2):
    for w in range(r):
        y = z3.Bool(f"m{w}_{a}_{b}")
        s.add(y == z3.Or([z3.And(x[w][a][g], x[w][b][g]) for g in range(ng)]))
        m[(w, a, b)] = y
    s.add(z3.PbEq([(m[(w, a, b)], 1) for w in range(r)], lam))
    s.add(z3.PbLe([(m[(w, a, b)], 1) for w in range(K)], 1))
    s.add(z3.PbGe([(m[(w, a, b)], 1) for w in range(C)], 1))
if lanes:
    lo, hi = r // ng, -(-r // ng)
    for p in P:
        for g in range(ng):
            t = [(x[w][p][g], 1) for w in range(r)]
            s.add(z3.PbGe(t, lo), z3.PbLe(t, hi))
t0 = time.time()
res = s.check()
print(f"v={v} K={K} C={C}: {res} in {time.time()-t0:.0f}s")
if res == z3.sat:
    mdl = s.model()
    weeks = []
    for w in range(r):
        gs = [[p + 1 for p in P if z3.is_true(mdl.eval(x[w][p][g]))] for g in range(ng)]
        weeks.append(gs)
    Path(__file__).with_name(f"design_v{v}_sat.json").write_text(json.dumps(weeks))
