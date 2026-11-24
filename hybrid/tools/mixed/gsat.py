"""Quotient z3 model for Z_m-symmetric mixed schedules with weeks of any stabiliser.
Points: orbits of sizes dividing m (g acts as +1 mod size inside each orbit).
A week spec d:g2,g3,g4 is a base week invariant under H = <g^(m/d)> (order d), developed into m/d copies.
usage: gsat.py m orbits a2 a3 a4 timeout spec...   orbits e.g. 12x3,1  (3 orbits of 12, one fixed point)
Writes JSON {weeks:[...]} (1-based) to stdout when sat."""
import sys, itertools, json, time, z3
m = int(sys.argv[1]); osz = []
for t in sys.argv[2].split(","):
    if "x" in t: s, k = map(int, t.split("x")); osz += [s] * k
    else: osz.append(int(t))
A = dict(zip((2, 3, 4), map(int, sys.argv[3:6]))); tmo = int(sys.argv[6])
specs = [(int(s.split(":")[0]), tuple(map(int, s.split(":")[1].split(",")))) for s in sys.argv[7:]]
start = []; v = 0
for s in osz: start.append(v); v += s
orb = [o for o, s in enumerate(osz) for _ in range(s)]
def g(p, i=1):
    o = orb[p]; return start[o] + (p - start[o] + i) % osz[o]
for d, t in specs: assert m % d == 0 and sum(k * s for k, s in zip(t, (2, 3, 4))) == v, (d, t)
pairs = list(itertools.combinations(range(v), 2)); porb = {}; orbs = []
for pq in pairs:
    if pq in porb: continue
    O = sorted({tuple(sorted((g(pq[0], i), g(pq[1], i)))) for i in range(m)}); k = len(orbs); orbs.append(O)
    for q in O: porb[q] = k
S = z3.SolverFor("QF_FD"); S.set("timeout", tmo * 1000)
def PbEq(L, k): return z3.PbEq(L, k) if L else z3.BoolVal(k == 0)
cov = [[] for _ in orbs]; fmt = {(o, s): [] for o in range(len(osz)) for s in (2, 3, 4)}
weekvars = []
for wi, (d, t) in enumerate(specs):
    step = m // d; cop = m // d
    inc = [[] for _ in range(v)]; X = []; bysize = {2: [], 3: [], 4: []}
    seen = set()
    for s in (2, 3, 4):
        if not t[s - 2]: continue
        for B in itertools.combinations(range(v), s):
            if B in seen: continue
            Os = []; cur = B
            while True:
                if cur in Os: break
                Os.append(cur); cur = tuple(sorted(g(p, step) for p in cur))
            for b in Os: seen.add(b)
            pts = [p for b in Os for p in b]
            if len(Os) > 1 and len(set(pts)) != len(pts): continue
            x = z3.Bool(f"w{wi}_{'_'.join(map(str, B))}"); X.append((x, Os))
            bysize[s].append((x, len(Os)))
            for p in pts: inc[p].append(x)
            pc = {}
            for b in Os:
                for pq in itertools.combinations(b, 2): pc[porb[pq]] = pc.get(porb[pq], 0) + 1
            for k, n in pc.items(): cov[k].append((x, n * cop))
            oc = {}
            for p in pts: oc[orb[p]] = oc.get(orb[p], 0) + 1
            for o, n in oc.items(): fmt[o, s].append((x, n * cop))
        S.add(PbEq(bysize[s], t[s - 2]))
    for p in range(v): S.add(PbEq([(l, 1) for l in inc[p]], 1))
    weekvars.append((d, X))
    print(f"week {wi} d={d} vars={len(X)}", file=sys.stderr)
for k, O in enumerate(orbs): S.add(PbEq(cov[k], len(O)))
for o in range(len(osz)):
    for s in (2, 3, 4):
        if fmt[o, s]: S.add(PbEq(fmt[o, s], A[s] * osz[o]))
        elif A[s]: S.add(z3.BoolVal(False))
t0 = time.time(); res = S.check(); print(res, f"{time.time()-t0:.1f}s", file=sys.stderr)
if res == z3.sat:
    M = S.model(); weeks = []
    for d, X in weekvars:
        base = [list(b) for x, Os in X if z3.is_true(M[x]) for b in Os]
        for i in range(m // d): weeks.append([[g(p, i) + 1 for p in B] for B in base])
    print(json.dumps({"m": m, "orbits": osz, "specs": specs, "weeks": weeks}))
else:
    sys.exit(1)
