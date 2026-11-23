"""Exact lane solve (z3 pseudo-boolean) for a Z_m x 4 lane-rotating design.

Input: a design line as printed by zsym (DUMP mode, "CAND BASE | ... TR ... HALF ...")
or by dfs40 (three lines BASE/TR/HALF). Base week w: block b goes to lane pi_w(b),
translate k to lane pi_w(b)+k. Transversal week f: translate k on lane r_f+k. Half week h:
its m blocks on a free permutation of the lanes. Every bowler on every lane floor/ceil.
Output: JSON list of weeks (each a list of m groups of point ids, lane order) or null.
Usage: python3 lanes_z3.py FILE [line_index] [timeout_s]
"""
import sys, json
import z3

PAIRING = [(0, 1, 2, 3), (0, 2, 1, 3), (0, 3, 1, 2)]


def parse(text):
    text = text.replace("\n", " ")
    t = text.split("BASE", 1)[1]
    basepart, rest = t.split("TR", 1)
    trpart, halfpart = rest.split("HALF", 1)
    base = [list(map(int, x.split())) for x in basepart.split("|") if x.strip()]
    tr = [list(map(int, x.split(","))) for x in trpart.split()]
    hb = [list(map(int, x.split(","))) for x in halfpart.split()]
    return base, tr, hb


def half_blocks(m, h, b, c):
    H = m // 2; P = PAIRING[h % 3]; out = []
    for side, off in ((0, b), (1, c)):
        x, y = P[2 * side], P[2 * side + 1]
        for t in range(H):
            out.append([m * x + t, m * x + t + H, m * y + (off + t) % m, m * y + (off + t + H) % m])
    return out


def expand(m, base, tr, hb, pi, rf, hl):
    W = []
    for w, bw in enumerate(base):
        for k in range(m):
            wk = [None] * m
            for b in range(m):
                wk[(pi[w][b] + k) % m] = [m * (p // m) + (p % m + k) % m for p in bw[4 * b:4 * b + 4]]
            W.append(wk)
    for h, (b, c) in enumerate(hb):
        wk = [None] * m
        for j, blk in enumerate(half_blocks(m, h, b, c)): wk[hl[h][j]] = blk
        W.append(wk)
    for f, cf in enumerate(tr):
        wk = [None] * m
        for k in range(m): wk[(rf[f] + k) % m] = [m * a + (cf[a] + k) % m for a in range(4)]
        W.append(wk)
    return W


def solve(m, base, tr, hb, timeout=600):
    V = 4 * m; r = len(base) * m + len(tr) + len(hb); lo, hi = r // m, -(-r // m)
    S = z3.Solver(); S.set("timeout", timeout * 1000)
    X = [[[z3.Bool(f"x{w}_{b}_{L}") for L in range(m)] for b in range(m)] for w in range(len(base))]
    R = [[z3.Bool(f"r{f}_{L}") for L in range(m)] for f in range(len(tr))]
    Y = [[[z3.Bool(f"y{h}_{j}_{L}") for L in range(m)] for j in range(m)] for h in range(len(hb))]
    one = lambda vs: S.add(z3.PbEq([(v, 1) for v in vs], 1))
    for w in range(len(base)):
        for b in range(m): one(X[w][b])
        for L in range(m): one([X[w][b][L] for b in range(m)])
    for f in range(len(tr)): one(R[f])
    for h in range(len(hb)):
        for j in range(m): one(Y[h][j])
        for L in range(m): one([Y[h][j][L] for j in range(m)])
    S.add(X[0][0][0])
    hblk = [half_blocks(m, h, b, c) for h, (b, c) in enumerate(hb)]
    for p in range(V):
        a, i = divmod(p, m)
        for L in range(m):
            terms = []
            for w, bw in enumerate(base):
                for b in range(m):
                    for q in bw[4 * b:4 * b + 4]:
                        if q // m == a: terms.append(X[w][b][(L - (i - q % m)) % m])
            for f, cf in enumerate(tr): terms.append(R[f][(L - (i - cf[a])) % m])
            for h in range(len(hb)):
                j = next(j for j, blk in enumerate(hblk[h]) if p in blk)
                terms.append(Y[h][j][L])
            S.add(z3.PbGe([(t, 1) for t in terms], lo)); S.add(z3.PbLe([(t, 1) for t in terms], hi))
    res = S.check()
    if res != z3.sat: return None, str(res)
    M = S.model(); val = lambda v: z3.is_true(M.eval(v))
    pi = [[next(L for L in range(m) if val(X[w][b][L])) for b in range(m)] for w in range(len(base))]
    rf = [next(L for L in range(m) if val(R[f][L])) for f in range(len(tr))]
    hl = [[next(L for L in range(m) if val(Y[h][j][L])) for j in range(m)] for h in range(len(hb))]
    return expand(m, base, tr, hb, pi, rf, hl), "sat"


if __name__ == "__main__":
    txt = open(sys.argv[1]).read()
    idx = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    to = int(sys.argv[3]) if len(sys.argv) > 3 else 600
    if "CAND" in txt:
        chunks = ["CAND" + c for c in txt.split("CAND")[1:]]
    else:
        chunks = ["BASE" + c for c in txt.split("BASE")[1:]]
    base, tr, hb = parse(chunks[idx])
    m = len(base[0]) // 4
    W, st = solve(m, base, tr, hb, to)
    print(st, file=sys.stderr)
    print(json.dumps({"m": m, "base": base, "tr": tr, "half": hb, "weeks": W}))
