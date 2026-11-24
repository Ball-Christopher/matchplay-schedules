"""v36 2-0-11 (URD({2,4};36) with r2 = 2) with a fixed-point-free automorphism of order 9.
Points (x, r) = r*9 + x, x in Z_9, r = 0..3.  Weeks:
  * one base 4-way class (9 blocks) developed mod 9            -> 9 four-way weeks
  * 2 four-way weeks, each the Z_9-orbit of a transversal block {(0,0),(a1,1),(a2,2),(a3,3)}
  * 2 two-way weeks, each 2 orbits of mixed edges {(x,r),(x+d,r')} with the four rows
    paired ({0,1}{2,3} / {0,2}{1,3} / {0,3}{1,2})
Every pair orbit (pure (r,d), d=1..4; mixed (r,r',d), d in Z_9) is covered exactly once.
z3 with one-hot choice variables for the fixed weeks.
usage: python3 v36_2011.py [timeout] [seed] [v36|v24]
  v24: Z_6 x 4 rows, one base class, one transversal-orbit 4-way week, 2-way weeks = all
  pure differences 3, and one mixed edge-orbit week (2-0-7)"""
import itertools, json, os, sys, time
import z3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cyclic import key, develop
HERE = os.path.dirname(os.path.abspath(__file__))
m, rows = 9, 4; V = 36; B = 9

def solve(timeout=600, seed=0, ntb=2, nmc=2, half=False, nbase=1):
    """ntb transversal-block weeks, nmc mixed 2-way weeks, half: one extra 2-way week of
    all pure differences m/2 (m even), nbase base 4-way classes."""
    s = z3.SolverFor('QF_FD'); s.set('timeout', timeout * 1000); s.set('random_seed', seed)
    byk = {}; XS = []
    for c in range(nbase):
        X = [[z3.Bool(f'x{c}_{b}_{p}') for p in range(V)] for b in range(B)]; XS.append(X)
        for p in range(V): s.add(z3.PbEq([(X[b][p], 1) for b in range(B)], 1))
        for b in range(B): s.add(z3.PbEq([(X[b][p], 1) for p in range(V)], 4))
        for p in range(V):
            for b in range(min(p + 1, B), B): s.add(z3.Not(X[b][p]))
        for b in range(1, B):
            for p in range(V): s.add(z3.Implies(X[b][p], z3.Or([X[b - 1][q] for q in range(p)] or [z3.BoolVal(False)])))
        for a, q in itertools.combinations(range(V), 2):
            kk = key(a, q, m, rows)
            for b in range(B):
                if m % 2 == 0 and kk[0] == 'p' and kk[2] == m // 2:
                    s.add(z3.Or(z3.Not(X[b][a]), z3.Not(X[b][q]))); continue
                t = z3.Bool(f't{c}_{b}_{a}_{q}'); s.add(t == z3.And(X[b][a], X[b][q])); byk.setdefault(kk, []).append(t)
    # transversal block candidates
    TB = {}
    for a1, a2, a3 in itertools.product(range(m), repeat=3):
        blk = [0, m + a1, 2 * m + a2, 3 * m + a3]
        TB[(a1, a2, a3)] = (z3.Bool(f'tb{a1}_{a2}_{a3}'), blk)
        for i, j in itertools.combinations(blk, 2): byk.setdefault(key(i, j, m, rows), []).append(TB[(a1, a2, a3)][0])
    s.add(z3.PbEq([(v, 1) for v, _ in TB.values()], ntb))
    pairings = [((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2))]
    MC = {}
    for pi, ((r1, r2), (r3, r4)) in enumerate(pairings):
        for d1, d2 in itertools.product(range(m), repeat=2):
            v_ = z3.Bool(f'mc{pi}_{d1}_{d2}'); MC[(pi, d1, d2)] = v_
            byk.setdefault(('m', r1, r2, d1), []).append(v_); byk.setdefault(('m', r3, r4, d2), []).append(v_)
    s.add(z3.PbEq([(v_, 1) for v_ in MC.values()], nmc))
    halfkeys = set(('p', r_, m // 2) for r_ in range(rows)) if half else set()
    for kk, ts in byk.items():
        if kk in halfkeys: s.add(z3.Not(z3.Or(ts)))
        else: s.add(z3.PbEq([(t, 1) for t in ts], 1))
    r = s.check()
    if r != z3.sat: return str(r)
    M = s.model()
    bases = [[[p for p in range(V) if z3.is_true(M.eval(X[b][p]))] for b in range(B)] for X in XS]
    tbs = [blk for (v_, blk) in TB.values() if z3.is_true(M.eval(v_))]
    mcs = [k for k, v_ in MC.items() if z3.is_true(M.eval(v_))]
    weeks = [[develop(b, t, m, rows) for b in base] for base in bases for t in range(m)]
    if half: weeks.append([[r_ * m + x, r_ * m + x + m // 2] for r_ in range(rows) for x in range(m // 2)])
    for blk in tbs: weeks.append([develop(blk, t, m, rows) for t in range(m)])
    for pi, d1, d2 in mcs:
        (r1, r2), (r3, r4) = pairings[pi]
        weeks.append([[r1 * m + x, r2 * m + (x + d1) % m] for x in range(m)] + [[r3 * m + x, r4 * m + (x + d2) % m] for x in range(m)])
    return [[[p + 1 for p in g] for g in wk] for wk in weeks]

if __name__ == '__main__':
    to = int(sys.argv[1]) if len(sys.argv) > 1 else 600; seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    cfg = sys.argv[3] if len(sys.argv) > 3 else 'v36'
    if cfg == 'v24':      # Z_6 x 4 rows: 6 + 1 four-way weeks, 2-way weeks: pure d=3 + one mixed
        m, rows, V, B = 6, 4, 24, 6; kw = dict(ntb=1, nmc=1, half=True)
    else: kw = {}
    t = time.time(); W = solve(to, seed, **kw)
    print(cfg, '2-0-x', 'found' if not isinstance(W, str) else W, round(time.time() - t, 1), flush=True)
    if not isinstance(W, str):
        from common import check_design
        check_design(V, W); json.dump(W, open(os.path.join(HERE, 'out', f'{cfg}_20x_{seed}.json'), 'w')); print('checked')
