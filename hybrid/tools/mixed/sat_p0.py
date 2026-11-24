"""Direct z3 block model with point-0 symmetry breaking: point 0's group in every week is fixed
({0} + the next consecutive labels), given the size of 0's group in each week.
usage: sat_p0.py v a2 a3 a4 timeout_s W1 W2 ...   each W = g2,g3,g4/s  (week type and size of 0's group)
Prints JSON weeks (1-based) when sat; exit 1 otherwise."""
import sys, itertools, json, z3, time
v = int(sys.argv[1]); a = tuple(map(int, sys.argv[2:5])); tmo = int(sys.argv[5])
types = []; zs = []; caps = []
args = sys.argv[6:]
while "--cap" in args:  # --cap g2,g3,g4:size:k  -> every point is in <= k groups of that size in weeks of that type
    i = args.index("--cap"); t, sz, k = args[i + 1].split(":"); caps.append((tuple(map(int, t.split(","))), int(sz), int(k))); del args[i:i + 2]
for s in args:
    t, z = s.split("/"); types.append(tuple(map(int, t.split(",")))); zs.append(int(z))
R = len(types); assert R == sum(a) and sum(z - 1 for z in zs) == v - 1
zg = []; nxt = 1
for z in zs: zg.append(tuple([0] + list(range(nxt, nxt + z - 1)))); nxt += z - 1
sizes = sorted({s for t in types for s, c in zip((2, 3, 4), t) if c})
S = z3.SolverFor("QF_FD"); S.set("timeout", tmo * 1000)
X = {}; inc = [[[] for _ in range(v)] for _ in range(R)]
pairv = {pq: [] for pq in itertools.combinations(range(v), 2)}; fmtv = [{s: [] for s in sizes} for _ in range(v)]
for pq in itertools.combinations(zg[0][:1] + tuple(range(1, v)), 2): pass
for w, t in enumerate(types):
    Z = set(zg[w])
    for s, cnt in zip((2, 3, 4), t):
        if not cnt: continue
        lits = []
        for B in itertools.combinations(range(1, v), s):
            if Z & set(B): continue
            x = z3.Bool(f"x{w}_{'_'.join(map(str, B))}"); X[w, B] = x; lits.append(x)
            for p in B: inc[w][p].append(x); fmtv[p][s].append(x)
            for pq in itertools.combinations(B, 2): pairv[pq].append(x)
        S.add(z3.PbEq([(l, 1) for l in lits], cnt - (len(zg[w]) == s)))
    for p in range(1, v):
        if p in Z: continue
        S.add(z3.PbEq([(l, 1) for l in inc[w][p]], 1))
    for pq in itertools.combinations(zg[w], 2): pairv[pq].append(True)
    for p in zg[w]: fmtv[p][len(zg[w])].append(True)
for pq, l in pairv.items():
    fixed = sum(1 for x in l if x is True); lits = [(x, 1) for x in l if x is not True]
    if fixed > 1: print("unsat (fixed)", file=sys.stderr); sys.exit(1)
    S.add(z3.PbEq(lits, 1 - fixed) if lits else z3.BoolVal(fixed == 1))
for p in range(v):
    for s in sizes:
        fixed = sum(1 for x in fmtv[p][s] if x is True); lits = [(x, 1) for x in fmtv[p][s] if x is not True]
        S.add(z3.PbEq(lits, a[s - 2] - fixed) if lits else z3.BoolVal(fixed == a[s - 2]))
for ct, sz, k in caps:
    for p in range(v):
        lits = [(x, 1) for (w, B), x in X.items() if types[w] == ct and len(B) == sz and p in B]
        fixed = sum(1 for w in range(R) if types[w] == ct and len(zg[w]) == sz and p in zg[w])
        S.add(z3.PbLe(lits, k - fixed) if lits else z3.BoolVal(fixed <= k))
t0 = time.time(); r = S.check(); print(r, f"{time.time()-t0:.1f}s", file=sys.stderr)
if r == z3.sat:
    M = S.model()
    weeks = [[[q + 1 for q in zg[ww]]] + [[q + 1 for q in B] for (w, B), x in X.items() if w == ww and z3.is_true(M[x])] for ww in range(R)]
    print(json.dumps(weeks))
else: sys.exit(1)
