"""z3 search for the 7-week part Y of round 2's 9-week covering, given X (2 weeks, from
out/xcands.json: clash-free against v18_oil's last block, first week transversal to the
owed-position classes).  Each couple at most once in Y, every couple not in X exactly
once; the couples of X that recur in Y then form a 1-factor F'.
avoid=1: no round-1 trio in Y.  tail=1: the first 5 weeks of Y avoid X's couples, so the
doubled couples' second meetings fall in Y's last 2 weeks (prefix spread).
usage: cover_z3.py cand seed tail avoid out.json [timeout_s]"""
import sys, json, time, itertools
from z3 import *
from common import *
ci, seed, tail, avoid, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
to = int(sys.argv[6]) if len(sys.argv) > 6 else 3000
X = [[tuple(t) for t in wk] for wk in json.load(open(os.path.join(HERE, "out/xcands.json")))[ci]["X"]]
XP = set(p for wk in X for p in pairs(wk))
T = [t for t in itertools.combinations(range(1, V + 1), 3) if not (avoid and t in R1T)]
tp = lambda t: list(itertools.combinations(t, 2))
s = SolverFor("QF_FD"); s.set("timeout", to * 1000); s.set("random_seed", seed)
NW = 7
x = [{t: Bool(f"x{w}_{t[0]}_{t[1]}_{t[2]}") for t in T if not (tail and w < 5 and any(e in XP for e in tp(t)))} for w in range(NW)]
for w in range(NW):
    for p in range(1, V + 1):
        s.add(PbEq([(l, 1) for t, l in x[w].items() if p in t], 1))
bypair = {e: [] for e in ALLP}
for w in range(NW):
    for t, l in x[w].items():
        for e in tp(t): bypair[e].append(l)
for e in ALLP:
    if e in XP: s.add(AtMost(*bypair[e], 1))
    else: s.add(PbEq([(l, 1) for l in bypair[e]], 1))
t0 = time.time(); r = s.check(); print(r, round(time.time() - t0, 1), file=sys.stderr)
if r == sat:
    m = s.model()
    weeks = [[list(t) for t in wk] for wk in X] + [[list(t) for t, l in x[w].items() if is_true(m[l])] for w in range(NW)]
    json.dump({"weeks": weeks, "tail": tail, "seed": seed, "cand": ci}, open(out, "w")); print("FOUND", out)
