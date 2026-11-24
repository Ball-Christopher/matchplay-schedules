"""Lane + position balancing for a raw mixed single round, then write hybrid/files/v{v}_{a}_mixed.json.
usage: finalize.py raw.json method [--n N] [--wrap] [--timeout S]
Lane pairs: each group gets a lane pair; with --wrap two 2-way groups may share one (wrapped).
Constraints: every bowler on every lane pair floor(R/n)..ceil(R/n) times; empty lane pairs spread evenly;
positions: within each format, each bowler's position counts differ by <=1 (z3)."""
import sys, json, itertools, collections, os, argparse, z3
ap = argparse.ArgumentParser(); ap.add_argument("raw"); ap.add_argument("method"); ap.add_argument("--n", type=int)
ap.add_argument("--wrap", action="store_true"); ap.add_argument("--timeout", type=int, default=120); ap.add_argument("--out")
ap.add_argument("--extra", default=""); ap.add_argument("--maxwrap", type=int, default=-1); ap.add_argument("--dir", default=None)
A = ap.parse_args()
d = json.load(open(A.raw)); W = d["weeks"]; v = max(p for wk in W for g in wk for p in g); R = len(W)
fmt = collections.Counter((p, len(g)) for wk in W for g in wk for p in g)
a = tuple(fmt[1, s] for s in (2, 3, 4))
n = A.n or max(len(wk) for wk in W)
lo, hi = R // n, -(-R // n)
def solve_lanes(n, wrap, exact=True):
    S = z3.Optimize() if not exact else z3.Solver(); S.set("timeout", A.timeout * 1000)
    y = {}
    for w, wk in enumerate(W):
        for gi, g in enumerate(wk):
            ls = [z3.Bool(f"y{w}_{gi}_{L}") for L in range(n)]
            for L in range(n): y[w, gi, L] = ls[L]
            S.add(z3.PbEq([(l, 1) for l in ls], 1))
        for L in range(n):
            big = [(y[w, gi, L], 2 if (len(g) > 2 or not wrap) else 1) for gi, g in enumerate(wk)]
            S.add(z3.PbLe(big, 2))
    for p in range(1, v + 1):
        for L in range(n):
            lits = [y[w, gi, L] for w, wk in enumerate(W) for gi, g in enumerate(wk) if p in g]
            if exact: S.add(z3.PbGe([(l, 1) for l in lits], lo), z3.PbLe([(l, 1) for l in lits], hi))
    # lane used in week w
    used = {}
    for w, wk in enumerate(W):
        for L in range(n):
            used[w, L] = z3.Or([y[w, gi, L] for gi in range(len(wk))])
    if wrap and A.maxwrap >= 0:
        S.add(z3.PbGe([(used[w, L], 1) for w in range(R) for L in range(n)], sum(len(wk) for wk in W) - A.maxwrap))
    empt = sum(n - min(n, len(wk)) for wk in W)  # approximate when no wrap
    if not wrap and empt:
        for L in range(n): S.add(z3.PbLe([(z3.Not(used[w, L]), 1) for w in range(R)], -(-empt // n)))
    r = S.check()
    if r != z3.sat: return None
    M = S.model(); out = []
    for w, wk in enumerate(W):
        lanes = [[] for _ in range(n)]
        for gi, g in enumerate(wk):
            for L in range(n):
                if z3.is_true(M[y[w, gi, L]]): lanes[L].append(gi)
        out.append(lanes)
    return out
lanes = solve_lanes(n, A.wrap)
exact = lanes is not None
if not exact:
    print("no lane-exact assignment found; using greedy fallback", file=sys.stderr)
    # fallback: minimise bowlers off via z3 Optimize-free heuristic: round-robin rotation
    lanes = []
    for w, wk in enumerate(W):
        L = [[] for _ in range(n)]
        for gi in range(len(wk)): L[(gi + w) % n].append(gi)
        lanes.append(L)
# positions
S = z3.Solver(); S.set("timeout", A.timeout * 1000); Z = {}
for w, wk in enumerate(W):
    for gi, g in enumerate(wk):
        k = len(g)
        for p in g:
            S.add(z3.PbEq([(z3.Bool(f"z{w}_{gi}_{p}_{i}"), 1) for i in range(k)], 1))
        for i in range(k):
            S.add(z3.PbEq([(z3.Bool(f"z{w}_{gi}_{p}_{i}"), 1) for p in g], 1))
for p in range(1, v + 1):
    for s in (2, 3, 4):
        lits = [(w, gi) for w, wk in enumerate(W) for gi, g in enumerate(wk) if p in g and len(g) == s]
        if not lits: continue
        c = len(lits); plo, phi = c // s, -(-c // s)
        for i in range(s):
            L = [(z3.Bool(f"z{w}_{gi}_{p}_{i}"), 1) for w, gi in lits]
            S.add(z3.PbGe(L, plo), z3.PbLe(L, phi))
pos_ok = S.check() == z3.sat
M = S.model() if pos_ok else None
def order(w, gi, g):
    if not pos_ok: return g
    res = [None] * len(g)
    for p in g:
        for i in range(len(g)):
            if z3.is_true(M[z3.Bool(f"z{w}_{gi}_{p}_{i}")]): res[i] = p
    return res
weeks = []
for w, wk in enumerate(W):
    row = []
    for L in range(n):
        gs = [order(w, gi, wk[gi]) for gi in lanes[w][L]]
        row.append(None if not gs else gs[0] if len(gs) == 1 else {"wrapped": gs})
    weeks.append(row)
name = A.out or f"v{v}_{a[0]}-{a[1]}-{a[2]}_mixed.json"
out = {"players": v, "lane_pairs": n, "weeks": weeks, "method": A.method + (" " + A.extra if A.extra else ""),
       "mix_2_3_4": list(a), "lane_exact": exact, "positions_balanced": pos_ok}
path = os.path.join(A.dir or os.path.join(os.path.dirname(__file__), "..", "..", "files"), name)
open(path, "w").write(json.dumps(out, indent=None).replace("], [", "],\n [") + "\n")
print(name, "lane_exact", exact, "positions", pos_ok)
