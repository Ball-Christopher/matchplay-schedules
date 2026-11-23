"""Finish round 2 from a covering file (weeks: X1, X2, Y1..Y7; 1-based trios).
 1. F' = couples met twice in X+Y.  Z = tau(A): v18_oil's NKTS block relabelled so its
    missing 1-factor F lands on F'; tau chosen by hill-climbing over the 9!*2^9 choices to
    minimise trios repeated from round 1 / X+Y.
 2. Week order: X1 (position-transversal) first; Y's weeks ordered so prefix spread is
    smallest; Z order by order search too.
 3. Lanes: z3 (QF_FD) picks a lane permutation per round-2 week so 34-week totals are 5/6.
 4. Positions: week 18 gives every bowler the position they are owed after round 1;
    weeks 19-34 by tools/positions.assign (fresh chunks of 3).
usage: finish.py cover.json outbase [seed]"""
import sys, json, itertools, random, time
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../../tools"))
from collections import Counter
from positions import assign
from common import *
from z3 import *
src, outbase = sys.argv[1], sys.argv[2]
rng = random.Random(int(sys.argv[3]) if len(sys.argv) > 3 else 1)
cov = [[tuple(sorted(t)) for t in wk] for wk in json.load(open(src))["weeks"]]
X, Y = cov[:2], cov[2:]
assert all(len({SHORT[p] for p in t}) == 3 for t in X[0])
cnt = Counter(p for wk in cov for p in pairs(wk))
assert set(cnt) == set(ALLP)
F2 = sorted(e for e in ALLP if cnt[e] == 2); assert len(F2) == 9 and len({p for e in F2 for p in e}) == 18
for blk in (C + X, Y):
    c = Counter(p for wk in blk for p in pairs(wk)); assert max(c.values()) == 1
# --- 1. Z = tau(A)
XYT = set(t for wk in cov for t in wk)
AT = [tuple(sorted(g)) for wk in A for g in wk]
def mk(order, flips):
    tau = {}
    for (a, b), j, f in zip(F, order, flips):
        c, d2 = F2[j]
        if f: c, d2 = d2, c
        tau[a] = c; tau[b] = d2
    return tau
def cost(tau): return sum(tuple(sorted(tau[p] for p in t)) in R1T or tuple(sorted(tau[p] for p in t)) in XYT for t in AT)
best = None
for restart in range(200):
    o = list(range(9)); rng.shuffle(o); fl = [rng.random() < .5 for _ in range(9)]
    cur = cost(mk(o, fl))
    for it in range(3000):
        if cur == 0: break
        o2, f2 = o[:], fl[:]
        if rng.random() < .5:
            i, j = rng.sample(range(9), 2); o2[i], o2[j] = o2[j], o2[i]
        else:
            i = rng.randrange(9); f2[i] = not f2[i]
        n = cost(mk(o2, f2))
        if n <= cur: o, fl, cur = o2, f2, n
    if best is None or cur < best[0]: best = (cur, mk(o, fl))
    if cur == 0: break
print("Z trios repeated from round 1 / X+Y:", best[0])
tau = best[1]
Z = [[tuple(sorted(tau[p] for p in g)) for g in wk] for wk in A]
c = Counter(p for wk in Z for p in pairs(wk)); assert max(c.values()) == 1 and not (set(c) & set(F2))
# --- 2. week order
def spreads(order):
    m = Counter({e: 2 for e in ALLP}); out = []
    for wk in order:
        m.update(pairs(wk)); out.append(max(m.values()) - min(m.values()))
    return out
key = lambda sp: (max(sp[:-1]), sum(x >= 2 for x in sp), sum(sp))
bestY = min((list(o) for o in itertools.permutations(Y)), key=lambda o: key(spreads(X + o + Z)))
R2 = X + bestY + Z
sp = spreads(R2); print("round-2 prefix spread", sp)
# --- 3. lanes
n, r = 6, 34; lo, hi = r // n, -(-r // n)
s = SolverFor("QF_FD"); s.set("timeout", 900000); s.set("random_seed", rng.randrange(10**6))
y = [[[Bool(f"y{w}_{g}_{l}") for l in range(n)] for g in range(n)] for w in range(17)]
for w in range(17):
    for g in range(n): s.add(PbEq([(y[w][g][l], 1) for l in range(n)], 1))
    for l in range(n): s.add(PbEq([(y[w][g][l], 1) for g in range(n)], 1))
for p in range(1, V + 1):
    gi = [next(g for g, t in enumerate(wk) if p in t) for wk in R2]
    for l in range(n):
        lits = [y[w][gi[w]][l] for w in range(17)]
        s.add(AtMost(*lits, hi - LANE1[p, l])); s.add(AtLeast(*lits, lo - LANE1[p, l]))
t0 = time.time(); res = s.check(); print("lanes", res, round(time.time() - t0, 1))
assert res == sat
m = s.model(); L2 = []
for w in range(17):
    row = [None] * n
    for g in range(n):
        for l in range(n):
            if is_true(m[y[w][g][l]]): row[l] = list(R2[w][g])
    L2.append(row)
# --- 4. positions
w18 = []
for g in L2[0]:
    row = [None] * 3
    for p in g: row[SHORT[p]] = p
    assert None not in row; w18.append(row)
P2 = [w18] + assign(L2[1:], 3)
full = R1 + P2
json.dump({"weeks": [[p for g in wk for p in g] for wk in full], "F2": F2, "repZ": best[0]}, open(outbase + ".raw.json", "w"))
print("wrote", outbase + ".raw.json")
