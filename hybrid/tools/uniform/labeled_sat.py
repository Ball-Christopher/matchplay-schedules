"""4-RGDD of type lam^u via a labeled resolvable design (Shen; Schuster 2009 Thm 2.2):
find a resolvable (u, 4, lam) design whose blocks carry Z_lam labels c_B(x) such that
for every pair {x, y} the lam blocks containing it have pairwise different label
differences c_B(y) - c_B(x).  Expanding x -> (x, 0..lam-1), block B -> blocks
{(x, j + c_B(x))}, j in Z_lam, gives 4-way weeks on lam*u points in which every couple
from different groups {(x, *)} meets exactly once.  The groups are then one more week of
lam-way groups.
  lam=2, u=16: 4-RGDD 2^16 -> v32 1-0-10
  lam=3, u=12: 4-RGDD 3^12 -> v36 0-1-11
usage: python3 labeled_sat.py u lam [timeout] [seed]"""
import itertools, json, os, sys, time
import z3
HERE = os.path.dirname(os.path.abspath(__file__))

def solve(u, lam, timeout=600, seed=0):
    k = 4; r = lam * (u - 1) // (k - 1); B = u // k
    s = z3.SolverFor('QF_FD'); s.set('timeout', timeout * 1000); s.set('random_seed', seed)
    X = [[[z3.Bool(f'x{c}_{b}_{a}') for a in range(u)] for b in range(B)] for c in range(r)]
    # label of point a in its block of class c: one-hot over Z_lam
    Lb = [[[z3.Bool(f'l{c}_{a}_{j}') for j in range(lam)] for a in range(u)] for c in range(r)]
    for c in range(r):
        for a in range(u):
            s.add(z3.PbEq([(X[c][b][a], 1) for b in range(B)], 1))
            s.add(z3.PbEq([(Lb[c][a][j], 1) for j in range(lam)], 1))
        for b in range(B): s.add(z3.PbEq([(X[c][b][a], 1) for a in range(u)], k))
        # symmetry inside a class: point a only in blocks <= a; block order by least point
        for a in range(u):
            for b in range(min(a + 1, B), B): s.add(z3.Not(X[c][b][a]))
        for b in range(1, B):
            for a in range(u):
                s.add(z3.Implies(X[c][b][a], z3.Or([X[c][b - 1][q] for q in range(a)] or [z3.BoolVal(False)])))
    # same-block indicator S[c][a][a'] and label difference
    for a, a2 in itertools.combinations(range(u), 2):
        for d in range(lam):
            terms = []
            for c in range(r):
                same = z3.Or([z3.And(X[c][b][a], X[c][b][a2]) for b in range(B)])
                diff = z3.Or([z3.And(Lb[c][a][j], Lb[c][a2][(j + d) % lam]) for j in range(lam)])
                t = z3.Bool(f't{a}_{a2}_{d}_{c}'); s.add(t == z3.And(same, diff)); terms.append((t, 1))
            s.add(z3.PbEq(terms, 1))
    # class 0: blocks {0..3},{4..7},...; point 0 always label 0 in every class
    for a in range(u): s.add(X[0][a // k][a])
    for c in range(r): s.add(Lb[c][0][0])
    # classes ordered by the partner set of point 0 is hard; order by block of point 1
    res = s.check()
    if res != z3.sat: return str(res)
    M = s.model()
    cls = []
    for c in range(r):
        blocks = []
        for b in range(B):
            pts = [a for a in range(u) if z3.is_true(M.eval(X[c][b][a]))]
            lab = [next(j for j in range(lam) if z3.is_true(M.eval(Lb[c][a][j]))) for a in pts]
            blocks.append((pts, lab))
        cls.append(blocks)
    return cls

def expand(u, lam, cls):
    P = lambda a, j: a * lam + (j % lam) + 1
    W = [[[P(a, j + l) for a, l in zip(pts, lab)] for pts, lab in blocks for j in range(lam)] for blocks in cls]
    W.append([[P(a, j) for j in range(lam)] for a in range(u)])
    return W

if __name__ == '__main__':
    u, lam = int(sys.argv[1]), int(sys.argv[2])
    to = int(sys.argv[3]) if len(sys.argv) > 3 else 600; seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    t = time.time(); r = solve(u, lam, to, seed)
    print(u, lam, 'found' if not isinstance(r, str) else r, round(time.time() - t, 1), flush=True)
    if not isinstance(r, str):
        sys.path.insert(0, HERE); from common import check_design
        W = expand(u, lam, r); check_design(u * lam, W)
        json.dump({'labeled': r, 'weeks': W}, open(os.path.join(HERE, 'out', f'labeled_{lam}^{u}_{seed}.json'), 'w'))
        print('expanded design checked', [len(w[0]) for w in W])
