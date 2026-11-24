"""Lane-exact assignment by annealing (alternative to finalize.py's z3 lanes), with as few wrapped 2-way pairs as asked.
usage: lanes_anneal.py raw.json method --n N [--wraps K] [--secs S] [--seed X] [--out name] [--dir D]
Each week w with g_w groups needs at least max(0, g_w - n) wraps; --wraps K (>= that total) lets the
annealer place up to K wraps in total (extra wraps go to weeks with the most 2-way groups).
Positions are then balanced by z3 exactly as in finalize.py. Writes hybrid/files/v{v}_{mix}_mixed.json (or --out)."""
import sys, json, random, math, time, collections, os, argparse, itertools, z3
ap = argparse.ArgumentParser(); ap.add_argument("raw"); ap.add_argument("method"); ap.add_argument("--n", type=int, required=True)
ap.add_argument("--wraps", type=int, default=-1); ap.add_argument("--secs", type=float, default=120); ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--out"); ap.add_argument("--dir"); ap.add_argument("--extra", default=""); ap.add_argument("--allow-off", action="store_true")
A = ap.parse_args(); rng = random.Random(A.seed)
d = json.load(open(A.raw)); W = d["weeks"]; R = len(W); n = A.n
v = max(p for wk in W for g in wk for p in g)
fmt = collections.Counter((p, len(g)) for wk in W for g in wk for p in g); a = tuple(fmt[1, s] for s in (2, 3, 4))
lo, hi = R // n, -(-R // n)
need = [max(0, len(wk) - n) for wk in W]
K = max(sum(need), A.wraps)
wr = list(need); extra = K - sum(need)
twos = [sum(1 for g in wk if len(g) == 2) for wk in W]
for w in sorted(range(R), key=lambda w: -twos[w]):
    while extra > 0 and wr[w] < twos[w] // 2 and len(W[w]) - wr[w] > 0 and wr[w] < twos[w] // 2: wr[w] += 1; extra -= 1
    if extra == 0: break
for w in range(R): assert 2 * wr[w] <= twos[w], f"week {w}: not enough 2-way groups to wrap"
# state per week: slots[L] = list of group indices (0, 1 or 2 two-way groups)
def init(w):
    g2 = [i for i, g in enumerate(W[w]) if len(g) == 2]; rest = [i for i, g in enumerate(W[w]) if len(g) != 2]
    rng.shuffle(g2); units = [[g2[2 * k], g2[2 * k + 1]] for k in range(wr[w])] + [[i] for i in g2[2 * wr[w]:]] + [[i] for i in rest]
    assert len(units) <= n; units += [[] for _ in range(n - len(units))]; rng.shuffle(units); return units
S = [init(w) for w in range(R)]
cnt = [[0] * n for _ in range(v + 1)]
def bowlers(w, u): return [p for gi in u for p in W[w][gi]]
for w in range(R):
    for L in range(n):
        for p in bowlers(w, S[w][L]): cnt[p][L] += 1
def pen(c): return (lo - c) if c < lo else (c - hi) if c > hi else 0
E = sum(pen(cnt[p][L]) for p in range(1, v + 1) for L in range(n))
def delta_move(w, L1, L2, b1, b2):
    """bowlers b1 leave L1 -> L2, b2 leave L2 -> L1"""
    ch = collections.Counter()
    for p in b1: ch[p, L1] -= 1; ch[p, L2] += 1
    for p in b2: ch[p, L2] -= 1; ch[p, L1] += 1
    dE = 0
    for (p, L), k in ch.items():
        if k: dE += pen(cnt[p][L] + k) - pen(cnt[p][L])
    return dE, ch
T = 1.0; t0 = time.time(); it = 0; best = E
while E > 0 and time.time() - t0 < A.secs:
    it += 1; w = rng.randrange(R); L1, L2 = rng.sample(range(n), 2); u1, u2 = S[w][L1], S[w][L2]
    if rng.random() < 0.3 and (len(u1) == 2 or len(u2) == 2):
        # swap one 2-way group of a wrapped slot with a single 2-way group elsewhere (or another wrapped one)
        if len(u1) != 2: L1, L2, u1, u2 = L2, L1, u2, u1
        cand = [k for k in range(len(u2)) if len(W[w][u2[k]]) == 2]
        if not cand: continue
        i, k = rng.randrange(2), rng.choice(cand)
        b1 = W[w][u1[i]]; b2 = W[w][u2[k]]
        dE, ch = delta_move(w, L1, L2, b1, b2)
        if dE <= 0 or rng.random() < math.exp(-dE / T):
            u1[i], u2[k] = u2[k], u1[i]
            for (p, L), kk in ch.items(): cnt[p][L] += kk
            E += dE
    else:
        dE, ch = delta_move(w, L1, L2, bowlers(w, u1), bowlers(w, u2))
        if dE <= 0 or rng.random() < math.exp(-dE / T):
            S[w][L1], S[w][L2] = u2, u1
            for (p, L), kk in ch.items(): cnt[p][L] += kk
            E += dE
    if it % 2000 == 0: T = max(0.15, T * 0.97)
    if it % 200000 == 0: T = 1.0
print("lane penalty", E, "iterations", it, file=sys.stderr)
if E > 0 and not A.allow_off: sys.exit(1)
# positions (as finalize.py)
Sv = z3.Solver(); Sv.set("timeout", 300000)
for w, wk in enumerate(W):
    for gi, g in enumerate(wk):
        k = len(g)
        for p in g: Sv.add(z3.PbEq([(z3.Bool(f"z{w}_{gi}_{p}_{i}"), 1) for i in range(k)], 1))
        for i in range(k): Sv.add(z3.PbEq([(z3.Bool(f"z{w}_{gi}_{p}_{i}"), 1) for p in g], 1))
for p in range(1, v + 1):
    for s in (2, 3, 4):
        lits = [(w, gi) for w, wk in enumerate(W) for gi, g in enumerate(wk) if p in g and len(g) == s]
        if not lits: continue
        c = len(lits); plo, phi = c // s, -(-c // s)
        for i in range(s):
            Lz = [(z3.Bool(f"z{w}_{gi}_{p}_{i}"), 1) for w, gi in lits]
            Sv.add(z3.PbGe(Lz, plo), z3.PbLe(Lz, phi))
pos_ok = Sv.check() == z3.sat; M = Sv.model() if pos_ok else None
def order(w, gi, g):
    if not pos_ok: return g
    res = [None] * len(g)
    for p in g:
        for i in range(len(g)):
            if z3.is_true(M[z3.Bool(f"z{w}_{gi}_{p}_{i}")]): res[i] = p
    return res
weeks = []
for w in range(R):
    row = []
    for L in range(n):
        gs = [order(w, gi, W[w][gi]) for gi in S[w][L]]
        row.append(None if not gs else gs[0] if len(gs) == 1 else {"wrapped": gs})
    weeks.append(row)
name = A.out or f"v{v}_{a[0]}-{a[1]}-{a[2]}_mixed.json"
out = {"players": v, "lane_pairs": n, "weeks": weeks, "method": A.method + (" " + A.extra if A.extra else ""),
       "mix_2_3_4": list(a), "lane_exact": E == 0, "positions_balanced": pos_ok, "wrapped": K}
path = os.path.join(A.dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "files"), name)
open(path, "w").write(json.dumps(out, indent=None).replace("], [", "],\n [") + "\n")
print(name, "wraps", K, "positions", pos_ok)
