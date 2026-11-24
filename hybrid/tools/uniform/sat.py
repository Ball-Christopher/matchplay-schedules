"""Direct z3 model for a uniform hybrid (URD): week w has groups of size ks[w].
x[w][p][g] <=> bowler p in group g of week w.  Symmetry breaking: week 0 fixed to
consecutive groups; in later weeks bowler 0 is in group 0 and groups are ordered by
their smallest member (bowler p can only be in groups 0..p).
usage: python3 sat.py v k1,k2,...  [timeout_s]   -> prints weeks (1-based) or UNSAT/UNKNOWN"""
import sys, itertools, json
import z3

def solve(v, ks, timeout=300, extra=None):
    R = len(ks); s = z3.SolverFor('QF_FD'); s.set('timeout', timeout * 1000)
    X = [[[z3.Bool(f'x{w}_{p}_{g}') for g in range(v // ks[w])] for p in range(v)] for w in range(R)]
    for w in range(R):
        G = v // ks[w]
        for p in range(v):
            s.add(z3.PbEq([(X[w][p][g], 1) for g in range(G)], 1))
        for g in range(G):
            s.add(z3.PbEq([(X[w][p][g], 1) for p in range(v)], ks[w]))
        if w == 0:
            for p in range(v): s.add(X[0][p][p // ks[0]])
        else:
            for p in range(v):
                for g in range(min(p + 1, G), G): s.add(z3.Not(X[w][p][g]))
            # group g's smallest member is > group g-1's smallest member: p in g -> some q<p in g-1
            for g in range(1, G):
                for p in range(v):
                    s.add(z3.Implies(X[w][p][g], z3.Or([X[w][q][g - 1] for q in range(p)] or [z3.BoolVal(False)])))
    # meet exactly once
    for a, b in itertools.combinations(range(v), 2):
        terms = []
        for w in range(R):
            for g in range(v // ks[w]):
                t = z3.Bool(f'm{w}_{a}_{b}_{g}')
                s.add(t == z3.And(X[w][a][g], X[w][b][g])); terms.append((t, 1))
        s.add(z3.PbEq(terms, 1))
    # week order symmetry: weeks of equal size sorted by bowler 1's partner set? keep simple:
    # among weeks of the same size (w>0), the group of bowler 1 (index 1) is non-decreasing
    if extra: extra(s, X)
    r = s.check()
    if r != z3.sat: return str(r)
    M = s.model(); out = []
    for w in range(R):
        G = v // ks[w]
        out.append([[p + 1 for p in range(v) if z3.is_true(M.eval(X[w][p][g]))] for g in range(G)])
    return out

if __name__ == '__main__':
    v = int(sys.argv[1]); ks = [int(k) for k in sys.argv[2].split(',')]
    to = int(sys.argv[3]) if len(sys.argv) > 3 else 300
    r = solve(v, ks, to)
    print(json.dumps(r) if not isinstance(r, str) else r)
