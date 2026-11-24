"""Quotient z3 model for Z_m-symmetric mixed schedules.
Points: class a in 0..c-1, x in Z_m -> id a*m+x; fixed j -> c*m+j. g: x->x+1 on classes.
Weeks: free base weeks (developed m times) and G-invariant weeks; both chosen by the solver.
usage: qsat.py m c f a2 a3 a4 timeout spec...   spec = F:g2,g3,g4 | I:g2,g3,g4
Output JSON {weeks:[...]} (1-based) to stdout."""
import sys, itertools, json, time, z3
m, c, f = map(int, sys.argv[1:4]); A = dict(zip((2,3,4), map(int, sys.argv[4:7]))); tmo = int(sys.argv[7])
specs = [(s[0], tuple(map(int, s[2:].split(",")))) for s in sys.argv[8:]]
v = c*m + f
def g(p, i=1): return p if p >= c*m else (p//m)*m + (p % m + i) % m
def orbit_set(S): return {frozenset(g(p, i) for p in S) for i in range(m)}
pairs = list(itertools.combinations(range(v), 2))
porb = {}; orbs = []
for pq in pairs:
    if pq in porb: continue
    O = sorted({tuple(sorted((g(pq[0], i), g(pq[1], i)))) for i in range(m)}); k = len(orbs); orbs.append(O)
    for q in O: porb[q] = k
ptorb = {}
for p in range(v): ptorb[p] = min(g(p, i) for i in range(m))
reps = sorted(set(ptorb.values())); orbsize = {r: len({g(r, i) for i in range(m)}) for r in reps}
sizes = [s for s in (2,3,4) if any(t[s-2] for _, t in specs)]
blocks = {s: list(itertools.combinations(range(v), s)) for s in sizes}
S = z3.SolverFor("QF_FD"); S.set("timeout", tmo*1000)
cov = [[] for _ in orbs]; fmt = {(r, s): [] for r in reps for s in sizes}
weekvars = []
for wi, (kind, t) in enumerate(specs):
    X = {}; inc = [[] for _ in range(v)]
    for s in sizes:
        cnt = t[s-2]; lits = []
        if not cnt: continue
        for B in blocks[s]:
            x = z3.Bool(f"w{wi}_{'_'.join(map(str,B))}"); X[B] = x; lits.append(x)
            for p in B: inc[p].append(x)
            pc = {}
            for pq in itertools.combinations(B, 2): pc[porb[pq]] = pc.get(porb[pq], 0) + 1
            for k, n in pc.items(): cov[k].append((x, n*m if kind == "F" else n))
            if kind == "F":
                for r in reps:
                    n = sum(1 for p in B if ptorb[p] == r)
                    if n: fmt[r, s].append((x, n*m//orbsize[r]))
            else:
                for r in reps:
                    if r in B: fmt[r, s].append((x, 1))
        S.add(z3.PbEq([(l, 1) for l in lits], cnt))
    for p in range(v): S.add(z3.PbEq([(l, 1) for l in inc[p]], 1))
    if kind == "I":
        for B, x in X.items():
            gB = tuple(sorted(g(p) for p in B)); S.add(x == X[gB])
    weekvars.append((kind, X))
for k, O in enumerate(orbs): S.add(z3.PbEq(cov[k], len(O)))
for r in reps:
    for s in sizes: S.add(z3.PbEq(fmt[r, s], A[s]) if fmt[r, s] else z3.BoolVal(A[s] == 0))
t0 = time.time(); res = S.check(); print(res, f"{time.time()-t0:.1f}s", file=sys.stderr)
if res == z3.sat:
    M = S.model(); weeks = []
    for kind, X in weekvars:
        base = [list(B) for B, x in X.items() if z3.is_true(M[x])]
        if kind == "F":
            for i in range(m): weeks.append([[g(p, i)+1 for p in B] for B in base])
        else: weeks.append([[p+1 for p in B] for B in base])
    print(json.dumps({"m": m, "c": c, "f": f, "specs": specs, "weeks": weeks}))
