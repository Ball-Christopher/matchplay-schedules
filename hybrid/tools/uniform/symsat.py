"""Direct z3 model for a uniform hybrid with a prescribed automorphism: a permutation sigma
of the bowlers and a permutation pi of the weeks (same block size along each cycle) such
that sigma maps the groups of week w onto the groups of week pi(w).  Encoded on the
"same group" variables: same(w, a, b) == same(pi(w), sigma(a), sigma(b)).
Presets (name: v, week sizes, sigma, pi):
  v24_207_z3   : Z_3 on 8 rows of 3, Q weeks (0 1 2)(3 4 5)(6), M weeks fixed
  v24_207_z4   : Z_4 on 6 rows of 4, Q weeks (0 1 2 3)(4 5)(6), M weeks fixed
  v24_207_z2   : Z_2 on 12 rows of 2, Q weeks (0 1)(2 3)(4 5)(6), M weeks fixed
  v24_207_z2s  : as z2 but the two M weeks swapped
  v24_207_z3b  : Z_3, Q weeks (0 1 2) and four fixed Q weeks, M weeks fixed
  v24_126_z3   : Z_3, weeks M, T T, Q x6 = (0 1 2)(3 4 5)
usage: python3 symsat.py preset [timeout] [seed]"""
import itertools, json, os, sys, time
import z3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))

def cyc_sigma(v, m):
    """(x, r) -> (x+1, r) on points r*m + x."""
    return [(p // m) * m + (p % m + 1) % m for p in range(v)]

def perm_from_cycles(n, cycles):
    pi = list(range(n))
    for c in cycles:
        for i, w in enumerate(c): pi[w] = c[(i + 1) % len(c)]
    return pi

PRESETS = {
 'v24_207_z3': (24, [4] * 7 + [2, 2], lambda: cyc_sigma(24, 3), [(0, 1, 2), (3, 4, 5)]),
 'v24_207_z4': (24, [4] * 7 + [2, 2], lambda: cyc_sigma(24, 4), [(0, 1, 2, 3), (4, 5)]),
 'v24_207_z2': (24, [4] * 7 + [2, 2], lambda: cyc_sigma(24, 2), [(0, 1), (2, 3), (4, 5)]),
 'v24_207_z2s': (24, [4] * 7 + [2, 2], lambda: cyc_sigma(24, 2), [(0, 1), (2, 3), (4, 5), (7, 8)]),
 'v24_207_z3b': (24, [4] * 7 + [2, 2], lambda: cyc_sigma(24, 3), [(0, 1, 2)]),
 'v24_207_z8': (24, [4] * 7 + [2, 2], lambda: cyc_sigma(24, 8), [(0, 1, 2, 3), (4, 5)]),
 'v24_126_z3': (24, [2, 3, 3] + [4] * 6, lambda: cyc_sigma(24, 3), [(3, 4, 5), (6, 7, 8)]),
 'v24_126_z2': (24, [2, 3, 3] + [4] * 6, lambda: cyc_sigma(24, 2), [(3, 4), (5, 6), (7, 8)]),
}

def solve(v, ks, sigma, pi, timeout=600, seed=0):
    R = len(ks); s = z3.SolverFor('QF_FD'); s.set('timeout', timeout * 1000); s.set('random_seed', seed)
    X = [[[z3.Bool(f'x{w}_{p}_{g}') for g in range(v // ks[w])] for p in range(v)] for w in range(R)]
    S = {}
    for w in range(R):
        G = v // ks[w]
        for p in range(v): s.add(z3.PbEq([(X[w][p][g], 1) for g in range(G)], 1))
        for g in range(G): s.add(z3.PbEq([(X[w][p][g], 1) for p in range(v)], ks[w]))
        for p in range(v):
            for g in range(min(p + 1, G), G): s.add(z3.Not(X[w][p][g]))
        for g in range(1, G):
            for p in range(v): s.add(z3.Implies(X[w][p][g], z3.Or([X[w][q][g - 1] for q in range(p)] or [z3.BoolVal(False)])))
        for a, b in itertools.combinations(range(v), 2):
            t = z3.Bool(f's{w}_{a}_{b}'); s.add(t == z3.Or([z3.And(X[w][a][g], X[w][b][g]) for g in range(G)])); S[(w, a, b)] = t
    sm = lambda w, a, b: S[(w, min(a, b), max(a, b))]
    for a, b in itertools.combinations(range(v), 2):
        s.add(z3.PbEq([(S[(w, a, b)], 1) for w in range(R)], 1))
        for w in range(R): s.add(S[(w, a, b)] == sm(pi[w], sigma[a], sigma[b]))
    r = s.check()
    if r != z3.sat: return str(r)
    M = s.model()
    return [[[p + 1 for p in range(v) if z3.is_true(M.eval(X[w][p][g]))] for g in range(v // ks[w])] for w in range(R)]

if __name__ == '__main__':
    name = sys.argv[1]; to = int(sys.argv[2]) if len(sys.argv) > 2 else 600; seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    v, ks, sg, cyc = PRESETS[name]
    t = time.time(); W = solve(v, ks, sg(), perm_from_cycles(len(ks), cyc), to, seed)
    print(name, 'found' if not isinstance(W, str) else W, round(time.time() - t, 1), flush=True)
    if not isinstance(W, str):
        from common import check_design
        check_design(v, W); json.dump(W, open(os.path.join(HERE, 'out', f'symsat_{name}_{seed}.json'), 'w')); print('checked')
