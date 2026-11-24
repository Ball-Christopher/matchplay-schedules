"""Direct z3 block model: variable per (week, candidate group). usage: sat_blocks.py v a2 a3 a4 timeout_s type=k ...
types written g2,g3,g4=k. First week fixed (symmetry breaking)."""
import sys, itertools, json, z3, time
v = int(sys.argv[1]); a = tuple(map(int, sys.argv[2:5])); tmo = int(sys.argv[5])
types = []
for s in sys.argv[6:]:
    t, k = s.split("="); types += [tuple(map(int, t.split(",")))] * int(k)
R = len(types); assert R == sum(a)
sizes = sorted({s for t in types for s, c in zip((2,3,4), t) if c})
blocks = {s: list(itertools.combinations(range(v), s)) for s in sizes}
S = z3.SolverFor("QF_FD"); S.set("timeout", tmo*1000)
X = {}
inc = [[[] for _ in range(v)] for _ in range(R)]; pairv = {pq: [] for pq in itertools.combinations(range(v), 2)}
fmtv = [{s: [] for s in sizes} for _ in range(v)]
for w, t in enumerate(types):
    for s, cnt in zip((2,3,4), t):
        if not cnt: continue
        lits = []
        for B in blocks[s]:
            x = z3.Bool(f"x{w}_{'_'.join(map(str,B))}"); X[w, B] = x; lits.append(x)
            for p in B: inc[w][p].append(x); fmtv[p][s].append(x)
            for pq in itertools.combinations(B, 2): pairv[pq].append(x)
        S.add(z3.PbEq([(l, 1) for l in lits], cnt))
for w in range(R):
    for p in range(v): S.add(z3.PbEq([(l, 1) for l in inc[w][p]], 1))
for pq, l in pairv.items(): S.add(z3.PbEq([(x, 1) for x in l], 1))
for p in range(v):
    for s in sizes: S.add(z3.PbEq([(x, 1) for x in fmtv[p][s]], a[s-2]))
# fix week 0
t = types[0]; p = 0
for s, cnt in zip((4,3,2), t[::-1]):
    for _ in range(cnt):
        S.add(X[0, tuple(range(p, p+s))]); p += s
t0 = time.time(); r = S.check(); print(r, f"{time.time()-t0:.1f}s", file=sys.stderr)
if r == z3.sat:
    M = S.model(); weeks = [[list(map(lambda q: q+1, B)) for (w, B), x in X.items() if w == ww and z3.is_true(M[x])] for ww in range(R)]
    print(json.dumps(weeks))
