"""z3 search for a 9-week resolvable covering of K18 (0-based points) with a prescribed
automorphism g (cycle type given), split X (2 weeks) + Y (7 weeks): each couple at most
once in X, at most once in Y, at least once overall.  Week orbits are given as
[length, role] with role 'X', 'E' (early Y) or 'L' (late Y); X + E must be clash-free
too, so that the doubled couples' second meetings all fall in the L weeks.
usage: sym_cover.py '[3,3,3,3,3,3]' '[[1,"X"],[1,"X"],[3,"E"],[1,"E"],[1,"E"],[1,"L"],[1,"L"]]' out.json seed [timeout]"""
import sys, json, itertools, time
from z3 import *
v = 18
cycles = json.loads(sys.argv[1]); worbits = json.loads(sys.argv[2]); out = sys.argv[3]; seed = int(sys.argv[4])
to = int(sys.argv[5]) if len(sys.argv) > 5 else 600
g = list(range(v)); pos = 0
for L in cycles:
    for i in range(L): g[pos + i] = pos + (i + 1) % L
    pos += L
assert pos == v
def powmap(k):
    m = list(range(v))
    for _ in range(k): m = [g[x] for x in m]
    return m
order = 1
while powmap(order) != list(range(v)): order += 1
P = [powmap(k) for k in range(order)]
T = list(itertools.combinations(range(v), 3))
img = lambda t, k: tuple(sorted(P[k % order][x] for x in t))
X = []
for o, (L, role) in enumerate(worbits):
    assert order % L == 0
    d = {}
    for t in T:
        if t in d: continue
        orb = set(); u = t
        while u not in orb: orb.add(u); u = img(u, L)
        ok = all(not (set(a) & set(c)) for a, c in itertools.combinations(orb, 2))
        var = Bool(f"x{o}_{t}") if ok else None
        for u in orb: d[u] = var
    X.append(d)
s = SolverFor("QF_FD"); s.set("timeout", to * 1000); s.set("random_seed", seed)
bypt = [[t for t in T if p in t] for p in range(v)]
for o in range(len(worbits)):
    for p in range(v):
        lits = list({l.get_id(): l for l in (X[o][t] for t in bypt[p]) if l is not None}.values())
        s.add(PbEq([(l, 1) for l in lits], 1))
for e in itertools.combinations(range(v), 2):
    by = {"X": [], "E": [], "L": []}
    for o, (L, role) in enumerate(worbits):
        for j in range(L):
            for p in range(v):
                if p in e: continue
                var = X[o][img(tuple(sorted(e + (p,))), order - j)]
                if var is not None: by[role].append(var)
    for grp in (by["X"], by["E"] + by["L"], by["X"] + by["E"]):
        if len(grp) > 1: s.add(AtMost(*grp, 1))
    s.add(Or(by["X"] + by["E"] + by["L"]))
t0 = time.time(); r = s.check(); print(r, round(time.time() - t0, 1), file=sys.stderr)
if r == sat:
    m = s.model(); weeks = []; roles = []
    for o, (L, role) in enumerate(worbits):
        w0 = sorted(set(t for t in T if X[o][t] is not None and is_true(m[X[o][t]])))
        for j in range(L):
            weeks.append(sorted(img(t, j) for t in w0)); roles.append(role)
    json.dump({"weeks": weeks, "roles": roles, "cycles": cycles}, open(out, "w")); print("FOUND", out)
