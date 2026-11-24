"""v24 0-1-7 with design and lanes found together, both invariant under Z_7.
Points (y, r) = r*7 + y (y in Z_7, r = 0..2) and inf_k = 21 + k.  3-way week: groups
{(x,0),(x,1),(x,2)} on lane pair x and {inf0, inf1, inf2} on lane pair 7 (= 'inf').
4-way weeks: one base class of 6 blocks developed mod 7; base block b sits on lane pair
lam_b (0..6 or 7 = inf), and in week t block b + t sits on lam_b + t (inf fixed).
Bowler (x, r) then plays lane pairs {lam_b(y,r) - y + x : y in Z_7}, so it is exact iff
for its row r the values lam_b(y,r) - y (y in Z_7) are distinct and avoid 0.  The block on
lane 'inf' must then hold one point of each row plus one inf point, and that inf bowler
is the only one off (it is on lane 'inf' every week).  Counting allows this: a lane pair
gets 3 + 4x visits, so >= 1 bowler is off, not >= 2.
usage: python3 eqlanes017.py [timeout] [seed] [rows required exact, e.g. 01]
(With all three rows the z3 model is unsat at once; with two rows the third row's
7 bowlers may be off.)"""
import itertools, json, os, sys, time
import z3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cyclic import key
HERE = os.path.dirname(os.path.abspath(__file__))
m, rows, f = 7, 3, 3; F = 21; V = 24; B = 6; NL = 8

def solve(timeout=600, seed=0, exact_rows=(0, 1, 2)):
    s = z3.SolverFor('QF_FD'); s.set('timeout', timeout * 1000); s.set('random_seed', seed)
    X = [[z3.Bool(f'x{b}_{p}') for p in range(V)] for b in range(B)]
    L = [[z3.Bool(f'l{b}_{l}') for l in range(NL)] for b in range(B)]
    for p in range(V): s.add(z3.PbEq([(X[b][p], 1) for b in range(B)], 1))
    for b in range(B):
        s.add(z3.PbEq([(X[b][p], 1) for p in range(V)], 4))
        s.add(z3.PbEq([(L[b][l], 1) for l in range(NL)], 1))
    for l in range(NL): s.add(z3.PbLe([(L[b][l], 1) for b in range(B)], 1))
    # symmetry: point p only in blocks <= p, blocks ordered by least point
    for p in range(V):
        for b in range(min(p + 1, B), B): s.add(z3.Not(X[b][p]))
    for b in range(1, B):
        for p in range(V): s.add(z3.Implies(X[b][p], z3.Or([X[b - 1][q] for q in range(p)] or [z3.BoolVal(False)])))
    # pair-orbit keys: exactly once; vertical (d=0 mixed) and inf-inf forbidden (3-way week)
    byk = {}
    for a, q in itertools.combinations(range(V), 2):
        kk = key(a, q, m, rows)
        bad = kk[0] == 'ii' or (kk[0] == 'm' and kk[3] == 0)
        for b in range(B):
            if bad: s.add(z3.Or(z3.Not(X[b][a]), z3.Not(X[b][q]))); continue
            t = z3.Bool(f't{b}_{a}_{q}'); s.add(t == z3.And(X[b][a], X[b][q])); byk.setdefault(kk, []).append(t)
    for kk, ts in byk.items(): s.add(z3.PbEq([(t, 1) for t in ts], 1))
    # lanes: for each row r and value w in 1..6 or inf, exactly one y gives it; never 0
    for r in exact_rows:
        vals = {w: [] for w in range(NL)}
        for y in range(m):
            p = r * m + y
            for b in range(B):
                for l in range(NL):
                    w = 7 if l == 7 else (l - y) % 7
                    t = z3.Bool(f'u{r}_{y}_{b}_{l}'); s.add(t == z3.And(X[b][p], L[b][l])); vals[w].append(t)
        for w in range(NL):
            if w == 0: s.add(z3.Not(z3.Or(vals[0])))
            else: s.add(z3.PbEq([(t, 1) for t in vals[w]], 1))
    r = s.check()
    if r != z3.sat: return str(r)
    M = s.model()
    blocks = [[p for p in range(V) if z3.is_true(M.eval(X[b][p]))] for b in range(B)]
    lam = [next(l for l in range(NL) if z3.is_true(M.eval(L[b][l]))) for b in range(B)]
    return blocks, lam

def develop(blocks, lam):
    sh = lambda p, t: p if p >= F else (p // m) * m + (p % m + t) % m
    weeks = []; slots = []
    T = [[r * m + x for r in range(rows)] for x in range(m)] + [[F, F + 1, F + 2]]
    weeks.append([[p + 1 for p in g] for g in T]); slots.append(list(range(8)))
    for t in range(m):
        wk = [[sh(p, t) + 1 for p in b] for b in blocks]; S = [-1] * NL
        for i, l in enumerate(lam): S[7 if l == 7 else (l + t) % 7] = i
        weeks.append(wk); slots.append(S)
    return weeks, slots

if __name__ == '__main__':
    to = int(sys.argv[1]) if len(sys.argv) > 1 else 600; seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    er = tuple(int(c) for c in sys.argv[3]) if len(sys.argv) > 3 else (0, 1, 2)
    t = time.time(); r = solve(to, seed, er)
    print('eqlanes017', 'found' if not isinstance(r, str) else r, round(time.time() - t, 1), flush=True)
    if not isinstance(r, str):
        W, S = develop(*r)
        json.dump({'weeks': W, 'slots': S, 'caps': [1] * 8, 'base': r}, open(os.path.join(HERE, 'out', f'eqlanes017_{seed}.json'), 'w'))
