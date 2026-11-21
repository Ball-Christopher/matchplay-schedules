"""v=16 lane pairs. Exact balance (each bowler 1-2 times per lane pair) is impossible
for AG(2,4): a lane pair holds one line per parallel class, 5 lines that pairwise
meet; covering all 16 points needs all 5 through one point (a pencil), and two
pencils share a line. With at most 3 per lane pair, a lane pair's 5 lines have at
most two triple points, so it misses >= 4 bowlers: >= 16 (bowler, lane-pair) zeros
in total. We minimise: cap per lane pair, then number of zero
(bowler, lane-pair) entries, then bowlers affected."""
import json, sys
from z3 import *
import lanes as L
def solve(weeks, cap):
    r, n = len(weeks), len(weeks[0])
    y = [[[Bool(f"y{w}_{g}_{l}") for l in range(n)] for g in range(n)] for w in range(r)]
    O = Optimize(); O.set("timeout", 300000)
    for w in range(r):
        for g in range(n): O.add(PbEq([(y[w][g][l], 1) for l in range(n)], 1))
        for l in range(n): O.add(PbEq([(y[w][g][l], 1) for g in range(n)], 1))
    for g in range(n): O.add(y[0][g][g])
    gof = {(w, p): g for w, wk in enumerate(weeks) for g, G in enumerate(wk) for p in G}
    zeros, offs = [], []
    for p in range(1, 17):
        zs = []
        for l in range(n):
            O.add(PbLe([(y[w][gof[(w, p)]][l], 1) for w in range(r)], cap))
            z = Bool(f"z{p}_{l}"); O.add(z == Not(Or([y[w][gof[(w, p)]][l] for w in range(r)]))); zs.append(z)
        zeros += zs; offs.append(Or(zs))
    # 16 zeros is the proven minimum under cap 3 (see module doc); require it,
    # then minimise bowlers affected
    O.add(PbLe([(z, 1) for z in zeros], 16))
    O.minimize(Sum([If(o, 1, 0) for o in offs]))
    if O.check() != sat: return None
    M = O.model()
    out = [[None] * n for _ in range(r)]
    for w in range(r):
        for g in range(n):
            for l in range(n):
                if is_true(M.evaluate(y[w][g][l])): out[w][l] = weeks[w][g]
    return out
if __name__ == "__main__":
    weeks = json.load(open("designs_raw.json"))["16"]["weeks"]
    for cap in (3,):
        out = solve(weeks, cap)
        if out:
            print("cap", cap, sorted(L.lane_counts(out).items())); json.dump(out, open("lanes16_out.json", "w")); break
        print("cap", cap, "infeasible")
