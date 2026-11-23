"""z3 search for round 2's 9-week covering (X = 2 weeks, Y = 7 weeks) with X free.
X's trios avoid the couples of v18_oil's last block C.  trans=1: X's first week is
transversal to the owed-position classes.  Each couple at most once in X, at most once
in Y, at least once overall.  avoid=1: no round-1 trio in Y (X may reuse them).
tail=1: X + first 5 weeks of Y clash-free.
usage: cover_joint.py seed trans tail avoid out.json [timeout_s]"""
import sys, json, time, itertools
from z3 import *
from common import *
seed, trans, tail, avoid, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
to = int(sys.argv[6]) if len(sys.argv) > 6 else 3000
tp = lambda t: list(itertools.combinations(t, 2))
TA = list(itertools.combinations(range(1, V + 1), 3))
T = [t for t in TA if not (avoid and t in R1T)]
TX = [t for t in TA if not any(p in CP for p in tp(t))]
TX1 = [t for t in TX if len({SHORT[p] for p in t}) == 3] if trans else TX
cand = [TX1, TX] + [T] * 7
s = SolverFor("QF_FD"); s.set("timeout", to * 1000); s.set("random_seed", seed)
x = [{t: Bool(f"x{w}_{t[0]}_{t[1]}_{t[2]}") for t in cand[w]} for w in range(9)]
for w in range(9):
    for p in range(1, V + 1):
        s.add(PbEq([(x[w][t], 1) for t in cand[w] if p in t], 1))
bypair = [{e: [] for e in ALLP} for _ in range(9)]
for w in range(9):
    for t in cand[w]:
        for e in tp(t): bypair[w][e].append(x[w][t])
for e in ALLP:
    X = bypair[0][e] + bypair[1][e]
    Y = [l for w in range(2, 9) for l in bypair[w][e]]
    if len(X) > 1: s.add(AtMost(*X, 1))
    s.add(AtMost(*Y, 1)); s.add(Or(X + Y))
    if tail:
        Y1 = [l for w in range(2, 7) for l in bypair[w][e]]
        s.add(AtMost(*(X + Y1), 1))
t0 = time.time(); r = s.check(); print(r, round(time.time() - t0, 1), file=sys.stderr)
if r == sat:
    m = s.model()
    weeks = [[list(t) for t in cand[w] if is_true(m[x[w][t]])] for w in range(9)]
    json.dump({"weeks": weeks, "tail": tail, "seed": seed}, open(out, "w")); print("FOUND", out)
