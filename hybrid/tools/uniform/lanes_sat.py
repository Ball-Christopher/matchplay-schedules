"""z3 lane assignment: minimise the number of bowlers whose lane counts are outside
[floor(R/n), ceil(R/n)].  Groups of 2-way weeks may share a lane pair (cap 2) when the
week has more matches than lane pairs.  Returns slots in the common.anneal_lanes format."""
import z3, itertools
def solve_lanes(v, weeks, n, K, timeout=120, fixed_off=None):
    R = len(weeks); lo, hi = R // n, -(-R // n)
    caps = [2 if (len(wk[0]) == 2 and len(wk) > n) else 1 for wk in weeks]
    s = z3.Solver(); s.set('timeout', timeout * 1000)
    Y = [[[z3.Bool(f'y{w}_{g}_{L}') for L in range(n)] for g in range(len(wk))] for w, wk in enumerate(weeks)]
    for w, wk in enumerate(weeks):
        for g in range(len(wk)): s.add(z3.PbEq([(Y[w][g][L], 1) for L in range(n)], 1))
        for L in range(n): s.add(z3.PbLe([(Y[w][g][L], 1) for g in range(len(wk))], caps[w]))
    off = [z3.Bool(f'off{p}') for p in range(v + 1)]
    for p in range(1, v + 1):
        for L in range(n):
            terms = [(Y[w][g][L], 1) for w, wk in enumerate(weeks) for g, grp in enumerate(wk) if p in grp]
            s.add(z3.Or(off[p], z3.And(z3.PbGe(terms, lo), z3.PbLe(terms, hi))))
    s.add(z3.PbLe([(off[p], 1) for p in range(1, v + 1)], K))
    # symmetry: week 0 group g on lane g (lanes are interchangeable)
    for g in range(min(len(weeks[0]), n)):
        if caps[0] == 1: s.add(Y[0][g][g])
    r = s.check()
    if r != z3.sat: return str(r), None
    M = s.model(); slots = []
    for w, wk in enumerate(weeks):
        S = [-1] * (n * caps[w]); fill = [0] * n
        for g in range(len(wk)):
            L = next(L for L in range(n) if z3.is_true(M.eval(Y[w][g][L])))
            S[L * caps[w] + fill[L]] = g; fill[L] += 1
        slots.append(S)
    return 'sat', (slots, caps)
