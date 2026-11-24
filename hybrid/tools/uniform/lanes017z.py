"""v24 0-1-7 lanes (R = n = 8: every bowler on every lane pair exactly once).  Exact is
impossible (a lane pair gets 3 + 4x visits, never 24); >= 2 bowlers off.  Here: choose the
off bowlers in advance and ask z3 for an assignment with every other bowler exact.
usage: python3 lanes017z.py <design json in out/ or 'file'> off1,off2,... [timeout] [extra_off_allowed]"""
import json, os, sys, itertools, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import z3
from regroup import load_weeks
HERE = os.path.dirname(os.path.abspath(__file__))

def solve(v, weeks, n, offs, timeout=600):
    R = len(weeks)
    s = z3.SolverFor('QF_FD'); s.set('timeout', timeout * 1000)
    Y = [[[z3.Bool(f'y{w}_{g}_{L}') for L in range(n)] for g in range(len(wk))] for w, wk in enumerate(weeks)]
    for w, wk in enumerate(weeks):
        for g in range(len(wk)): s.add(z3.PbEq([(Y[w][g][L], 1) for L in range(n)], 1))
        for L in range(n): s.add(z3.PbLe([(Y[w][g][L], 1) for g in range(len(wk))], 1))
    lo, hi = R // n, -(-R // n)
    for p in range(1, v + 1):
        if p in offs: continue
        for L in range(n):
            terms = [(Y[w][g][L], 1) for w, wk in enumerate(weeks) for g, grp in enumerate(wk) if p in grp]
            s.add(z3.PbGe(terms, lo)); s.add(z3.PbLe(terms, hi))
    w0 = max(range(R), key=lambda w: len(weeks[w]))
    for g in range(min(len(weeks[w0]), n)): s.add(Y[w0][g][g])
    r = s.check()
    if r != z3.sat: return str(r)
    M = s.model(); slots = []
    for w, wk in enumerate(weeks):
        S = [-1] * n
        for g in range(len(wk)):
            S[next(L for L in range(n) if z3.is_true(M.eval(Y[w][g][L])))] = g
        slots.append(S)
    return slots

if __name__ == '__main__':
    src = sys.argv[1]
    if src == 'file': v, W = load_weeks('v24_0-1-7.json')
    else: W = json.load(open(os.path.join(HERE, 'out', src))); v = 24
    W = sorted(W, key=lambda wk: -len(wk[0]))
    offs = set(int(x) for x in sys.argv[2].split(','))
    to = int(sys.argv[3]) if len(sys.argv) > 3 else 600
    t = time.time(); r = solve(v, W, 8, offs, to)
    print(src, sorted(offs), r if isinstance(r, str) else 'sat', round(time.time() - t, 1), flush=True)
    if not isinstance(r, str):
        json.dump({'weeks': W, 'slots': r}, open(os.path.join(HERE, 'out', f'lanes017z_{"_".join(map(str, sorted(offs)))}.json'), 'w'))
