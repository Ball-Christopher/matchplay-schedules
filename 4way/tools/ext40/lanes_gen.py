"""General exact lane solve (z3 PB): reorder the groups of each week so every bowler is on
every lane pair floor/ceil times.  Used for 40 (Z_13 x 3 u inf design, no lane symmetry).
Usage: python3 lanes_gen.py BASEFILE line timeout_s  (base week line from dfs13) -> JSON weeks"""
import sys, json, z3

def develop13(b):
    G = [b[i:i + 4] for i in range(0, 40, 4)]
    return [[[39 if x == 39 else 13 * (x // 13) + (x % 13 + k) % 13 for x in g] for g in G] for k in range(13)]

def solve(W, v, timeout):
    n = len(W[0]); r = len(W); lo, hi = r // n, -(-r // n)
    S = z3.Solver(); S.set("timeout", timeout * 1000)
    Y = [[[z3.Bool(f"y{w}_{g}_{L}") for L in range(n)] for g in range(n)] for w in range(r)]
    for w in range(r):
        for g in range(n): S.add(z3.PbEq([(Y[w][g][L], 1) for L in range(n)], 1))
        for L in range(n): S.add(z3.PbEq([(Y[w][g][L], 1) for g in range(n)], 1))
    S.add(Y[0][0][0])
    where = {}
    for w, wk in enumerate(W):
        for g, grp in enumerate(wk):
            for p in grp: where[(p, w)] = g
    for p in range(v):
        for L in range(n):
            t = [(Y[w][where[(p, w)]][L], 1) for w in range(r)]
            S.add(z3.PbGe(t, lo)); S.add(z3.PbLe(t, hi))
    res = S.check()
    if res != z3.sat: return None, str(res)
    M = S.model()
    out = []
    for w, wk in enumerate(W):
        o = [None] * n
        for g in range(n):
            o[next(L for L in range(n) if z3.is_true(M.eval(Y[w][g][L])))] = wk[g]
        out.append(o)
    return out, "sat"

if __name__ == "__main__":
    lines = open(sys.argv[1]).read().split("\n")
    b = list(map(int, lines[int(sys.argv[2])].split()))
    W, st = solve(develop13(b), 40, int(sys.argv[3]))
    print(st, file=sys.stderr)
    print(json.dumps({"base": b, "weeks": W}))
