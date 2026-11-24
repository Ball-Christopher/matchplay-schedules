"""z3 version of the cyclic base-class search (same templates as cyclic.py):
x[c][b][p] = point p in block b of base class c; every pair-orbit key not used by the
fixed weeks is hit exactly once by the base classes (forbidden ones never).
usage: python3 cyclic_sat.py <case> [timeout]  (cases from try_cyclic.py / try_rows.py)"""
import os, sys, itertools, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import z3
from cyclic import key, develop
def solve(m, rows, f, ks, fixed, timeout=600):
    F = rows * m; V = F + f
    forb = set()
    for wk in fixed:
        for g in wk:
            for a, b in itertools.combinations(g, 2): forb.add(key(a, b, m, rows))
    s = z3.SolverFor('QF_FD'); s.set('timeout', timeout * 1000)
    X = []; byk = {}
    for c, k in enumerate(ks):
        B = V // k; Xc = [[z3.Bool(f'x{c}_{b}_{p}') for p in range(V)] for b in range(B)]; X.append(Xc)
        for p in range(V): s.add(z3.PbEq([(Xc[b][p], 1) for b in range(B)], 1))
        for b in range(B): s.add(z3.PbEq([(Xc[b][p], 1) for p in range(V)], k))
        # symmetry: point p only in blocks 0..p, block b's least point > block b-1's least point
        for p in range(V):
            for b in range(min(p + 1, B), B): s.add(z3.Not(Xc[b][p]))
        for b in range(1, B):
            for p in range(V): s.add(z3.Implies(Xc[b][p], z3.Or([Xc[b - 1][q] for q in range(p)] or [z3.BoolVal(False)])))
        for b in range(B):
            for a, q in itertools.combinations(range(V), 2):
                kk = key(a, q, m, rows)
                bad = kk[0] == 'ii' or kk in forb or (kk[0] == 'p' and m % 2 == 0 and kk[2] == m // 2)
                if bad: s.add(z3.Or(z3.Not(Xc[b][a]), z3.Not(Xc[b][q]))); continue
                t = z3.Bool(f't{c}_{b}_{a}_{q}'); s.add(t == z3.And(Xc[b][a], Xc[b][q]))
                byk.setdefault(kk, []).append(t)
    for kk, ts in byk.items(): s.add(z3.PbEq([(t, 1) for t in ts], 1))
    r = s.check()
    if r != z3.sat: return str(r)
    M = s.model(); weeks = [list(map(list, w)) for w in fixed]
    for c, k in enumerate(ks):
        cl = [[p for p in range(V) if z3.is_true(M.eval(X[c][b][p]))] for b in range(V // k)]
        for t in range(m): weeks.append([develop(b, t, m, rows) for b in cl])
    return weeks
if __name__ == '__main__':
    name = sys.argv[1]; to = int(sys.argv[2]) if len(sys.argv) > 2 else 600
    import try_rows
    if name in try_rows.CASES:
        m, rows, ks, fx = try_rows.CASES[name]; f = 0; fx = fx()
    else:
        sys.argv = sys.argv[:1]; import try_cyclic
        m, rows, f, ks, half = try_cyclic.cases[name]
        fx = [] if half is None else try_cyclic.groups_fixed(m, rows, f, half)
    t = time.time(); W = solve(m, rows, f, ks, fx, to)
    print(name, 'found' if not isinstance(W, str) else 'NOT found: ' + W, round(time.time() - t, 1), flush=True)
    if not isinstance(W, str): print(W)
