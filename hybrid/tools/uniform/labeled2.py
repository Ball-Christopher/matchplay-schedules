"""Labeled uniformly resolvable GDDs (Shen; Schuster 2009 Thm 2.2) by z3, general version.
Quotient points 0..u-1 with groups of size g (consecutive); classes with given block
sizes; each block carries Z_lam labels; for every pair {x, y} from different groups and
every d in Z_lam exactly one block contains x, y with label difference d.  Expanding by
lam gives a uniform resolvable GDD on lam*u points with groups of size lam*g; the groups
are added as one more week (group size lam*g must be 2, 3 or 4).
  v24 2-0-7:  u=12 g=1 lam=2 sizes 2 + 4x7  (groups -> 2nd 2-way week)
              u=12 g=2 lam=2 sizes 2x2 + 4x6 (groups -> 7th 4-way week)
  v32 1-0-10: u=16 g=2 lam=2 sizes 2 + 4x9;  u=16 g=1 lam=2 sizes 4x10
  v36 0-1-11: u=12 g=1 lam=3 sizes 4x11
usage: python3 labeled2.py u g lam sizes(e.g. 2,4,4,4) [timeout] [seed] [tag]"""
import itertools, json, os, sys, time
import z3
HERE = os.path.dirname(os.path.abspath(__file__))

def solve(u, g, lam, sizes, timeout=600, seed=0):
    r = len(sizes); grp = lambda a: a // g
    s = z3.SolverFor('QF_FD'); s.set('timeout', timeout * 1000); s.set('random_seed', seed)
    X = []; L = []
    for c, k in enumerate(sizes):
        B = u // k
        Xc = [[z3.Bool(f'x{c}_{b}_{a}') for a in range(u)] for b in range(B)]; X.append(Xc)
        L.append([[z3.Bool(f'l{c}_{a}_{j}') for j in range(lam)] for a in range(u)])
        for a in range(u):
            s.add(z3.PbEq([(Xc[b][a], 1) for b in range(B)], 1))
            s.add(z3.PbEq([(L[c][a][j], 1) for j in range(lam)], 1))
            for b in range(min(a + 1, B), B): s.add(z3.Not(Xc[b][a]))
        for b in range(B):
            s.add(z3.PbEq([(Xc[b][a], 1) for a in range(u)], k))
            if b:
                for a in range(u):
                    s.add(z3.Implies(Xc[b][a], z3.Or([Xc[b - 1][q] for q in range(a)] or [z3.BoolVal(False)])))
        # point 0 has label 0 in every class (labels are defined up to a shift per block)
        s.add(L[c][0][0])
        # two points of the same group never share a block
        for b in range(B):
            for a, a2 in itertools.combinations(range(u), 2):
                if grp(a) == grp(a2): s.add(z3.Or(z3.Not(Xc[b][a]), z3.Not(Xc[b][a2])))
    for a, a2 in itertools.combinations(range(u), 2):
        if grp(a) == grp(a2): continue
        for d in range(lam):
            terms = []
            for c, k in enumerate(sizes):
                same = z3.Or([z3.And(X[c][b][a], X[c][b][a2]) for b in range(u // k)])
                diff = z3.Or([z3.And(L[c][a][j], L[c][a2][(j + d) % lam]) for j in range(lam)])
                t = z3.Bool(f't{a}_{a2}_{d}_{c}'); s.add(t == z3.And(same, diff)); terms.append((t, 1))
            s.add(z3.PbEq(terms, 1))
    # symmetry: the first class of the largest size has blocks of consecutive group-transversals is
    # not forced (groups make that awkward); keep it simple.
    res = s.check()
    if res != z3.sat: return str(res)
    M = s.model(); cls = []
    for c, k in enumerate(sizes):
        blocks = []
        for b in range(u // k):
            pts = [a for a in range(u) if z3.is_true(M.eval(X[c][b][a]))]
            blocks.append((pts, [next(j for j in range(lam) if z3.is_true(M.eval(L[c][a][j]))) for a in pts]))
        cls.append(blocks)
    return cls

def expand(u, g, lam, cls):
    P = lambda a, j: a * lam + (j % lam) + 1
    W = [[[P(a, j + l) for a, l in zip(pts, lab)] for pts, lab in blocks for j in range(lam)] for blocks in cls]
    W.append([[P(a, j) for a in range(h * g, h * g + g) for j in range(lam)] for h in range(u // g)])
    return W

if __name__ == '__main__':
    u, g, lam = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    sizes = [int(x) for x in sys.argv[4].split(',')]
    to = int(sys.argv[5]) if len(sys.argv) > 5 else 600; seed = int(sys.argv[6]) if len(sys.argv) > 6 else 0
    tag = sys.argv[7] if len(sys.argv) > 7 else f'{u}_{g}_{lam}'
    t = time.time(); r = solve(u, g, lam, sizes, to, seed)
    print(tag, 'found' if not isinstance(r, str) else r, round(time.time() - t, 1), flush=True)
    if not isinstance(r, str):
        sys.path.insert(0, HERE); from common import check_design
        W = expand(u, g, lam, r); check_design(u * lam, W)
        json.dump({'u': u, 'g': g, 'lam': lam, 'labeled': r, 'weeks': W}, open(os.path.join(HERE, 'out', f'lab2_{tag}_{seed}.json'), 'w'))
        print('expanded design checked', sorted(len(w[0]) for w in W))
