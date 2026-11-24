"""Quotient z3 model for schedules invariant under a finite group G acting regularly on c point orbits (+ f fixed points).
Each week spec 'k:g2,g3,g4' is a base week invariant under subgroup number k (see --list), developed over coset reps of G/H.
usage: ggsat.py GROUP c f a2 a3 a4 timeout spec...      ggsat.py GROUP --list
GROUP: Z<n>, Z<a>xZ<b>, S3, A4, D<n> (dihedral order 2n), Dic3, Q8.
Prints JSON {weeks} to stdout when sat (1-based ids); exit 1 otherwise."""
import sys, itertools, json, time, z3
def perm_group(gens):
    n = len(gens[0]); e = tuple(range(n)); els = [e]; seen = {e}; i = 0
    while i < len(els):
        for g in gens:
            h = tuple(g[x] for x in els[i])
            if h not in seen: seen.add(h); els.append(h)
        i += 1
    return els
def cyc(n, k): return tuple((x + k) % n for x in range(n))
def make(name):
    if name.startswith("Z") and "x" in name:
        a, b = map(int, name.replace("Z", "").split("x")); n = a * b
        return perm_group([tuple(((x // b + 1) % a) * b + x % b for x in range(n)), tuple((x // b) * b + (x % b + 1) % b for x in range(n))])
    if name.startswith("Z"): n = int(name[1:]); return perm_group([cyc(n, 1)])
    if name.startswith("D") and name != "Dic3": n = int(name[1:]); return perm_group([cyc(n, 1), tuple((-x) % n for x in range(n))])
    if name == "S3": return perm_group([(1, 0, 2), (1, 2, 0)])
    if name == "A4": return perm_group([(1, 2, 0, 3), (1, 0, 3, 2)])
    if name == "Dic3":  # <a,x | a^6, x^2=a^3, x a x^-1 = a^-1> as perms on 12 points via regular rep of generated words
        # realise as subgroup of S_12 by right-regular action computed from a 2x2 complex-free presentation: use matrices mod 7
        A = ((3, 0), (0, 5)); X = ((0, 6), (1, 0))  # over GF(7): A order 6, X^2 = -I = A^3, X A X^-1 = A^-1
        def mul(P, Q): return tuple(tuple(sum(P[i][k] * Q[k][j] for k in range(2)) % 7 for j in range(2)) for i in range(2))
        I = ((1, 0), (0, 1)); els = [I]; i = 0
        while i < len(els):
            for g in (A, X):
                h = mul(els[i], g)
                if h not in els: els.append(h)
            i += 1
        idx = {m: j for j, m in enumerate(els)}
        return perm_group([tuple(idx[mul(g, m)] for m in els) for g in (A, X)])
    if name == "Q8":
        return make_from_mats([((0, 6), (1, 0)), ((2, 2), (2, 5))], 7)
    raise SystemExit("unknown group")
def make_from_mats(gens, p):
    def mul(P, Q): return tuple(tuple(sum(P[i][k] * Q[k][j] for k in range(2)) % p for j in range(2)) for i in range(2))
    I = ((1, 0), (0, 1)); els = [I]; i = 0
    while i < len(els):
        for g in gens:
            h = mul(els[i], g)
            if h not in els: els.append(h)
        i += 1
    idx = {m: j for j, m in enumerate(els)}
    return perm_group([tuple(idx[mul(g, m)] for m in els) for g in gens])
G0 = make(sys.argv[1]); k = len(G0)
# regular representation: element index -> left multiplication perm on element indices
eidx = {g: i for i, g in enumerate(G0)}
def comp(g, h): return tuple(g[h[x]] for x in range(len(h)))  # g after h
L = [[eidx[comp(g, h)] for h in G0] for g in G0]  # L[g][h] = index of g*h
subs = []
for r in (2, 3, 4, 6):
    for S in itertools.combinations(range(1, k), r - 1):
        H = frozenset((0,) + S)
        if all(L[a][b] in H for a in H for b in H) and H not in subs: subs.append(H)
if sys.argv[2] == "--list":
    for i, H in enumerate(subs): print(i, len(H), sorted(H))
    sys.exit()
c, f = int(sys.argv[2]), int(sys.argv[3]); A = dict(zip((2, 3, 4), map(int, sys.argv[4:7]))); tmo = int(sys.argv[7])
specs = [(int(s.split(":")[0]), tuple(map(int, s.split(":")[1].split(",")))) for s in sys.argv[8:]]
v = c * k + f
def act(gi, p): return p if p >= c * k else (p // k) * k + L[gi][p % k]
orb = [p // k if p < c * k else c + p - c * k for p in range(v)]
osz = [k] * c + [1] * f
pairs = list(itertools.combinations(range(v), 2)); porb = {}; orbs = []
for pq in pairs:
    if pq in porb: continue
    O = sorted({tuple(sorted((act(gi, pq[0]), act(gi, pq[1])))) for gi in range(k)}); j = len(orbs); orbs.append(O)
    for q in O: porb[q] = j
S = z3.SolverFor("QF_FD"); S.set("timeout", tmo * 1000)
def PbEq(Lst, n): return z3.PbEq(Lst, n) if Lst else z3.BoolVal(n == 0)
cov = [[] for _ in orbs]; fmt = {(o, s): [] for o in range(len(osz)) for s in (2, 3, 4)}; weekvars = []
for wi, (hi, t) in enumerate(specs):
    H = sorted(subs[hi]) if hi >= 0 else [0]
    reps = []; covered = set()
    for gi in range(k):
        if gi in covered: continue
        reps.append(gi); covered |= {L[gi][h] for h in H}
    cop = len(reps); inc = [[] for _ in range(v)]; X = []; seen = set()
    for s in (2, 3, 4):
        if not t[s - 2]: continue
        bys = []
        for B in itertools.combinations(range(v), s):
            if B in seen: continue
            Os = sorted({tuple(sorted(act(h, p) for p in B)) for h in H})
            seen.update(Os); pts = [p for b in Os for p in b]
            if len(set(pts)) != len(pts): continue
            x = z3.Bool(f"w{wi}_{'_'.join(map(str, B))}"); X.append((x, Os)); bys.append((x, len(Os)))
            for p in pts: inc[p].append(x)
            pc = {}
            for b in Os:
                for pq in itertools.combinations(b, 2): pc[porb[pq]] = pc.get(porb[pq], 0) + 1
            for j, n in pc.items(): cov[j].append((x, n * cop))
            oc = {}
            for p in pts: oc[orb[p]] = oc.get(orb[p], 0) + 1
            for o, n in oc.items(): fmt[o, s].append((x, n * cop))
        S.add(PbEq(bys, t[s - 2]))
    for p in range(v): S.add(PbEq([(l, 1) for l in inc[p]], 1))
    weekvars.append((reps, X)); print(f"week {wi} |H|={len(H)} copies={cop} vars={len(X)}", file=sys.stderr)
for j, O in enumerate(orbs): S.add(PbEq(cov[j], len(O)))
for o in range(len(osz)):
    for s in (2, 3, 4):
        if fmt[o, s]: S.add(PbEq(fmt[o, s], A[s] * osz[o]))
        elif A[s]: S.add(z3.BoolVal(False))
t0 = time.time(); res = S.check(); print(res, f"{time.time()-t0:.1f}s", file=sys.stderr)
if res == z3.sat:
    M = S.model(); weeks = []
    for reps, X in weekvars:
        base = [list(b) for x, Os in X if z3.is_true(M[x]) for b in Os]
        for gi in reps: weeks.append([[act(gi, p) + 1 for p in B] for B in base])
    print(json.dumps({"group": sys.argv[1], "specs": specs, "weeks": weeks}))
else: sys.exit(1)
