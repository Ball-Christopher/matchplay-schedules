"""Finish the 32/36/40 4-way files from the raw designs found by zsym / dfs40 / lanes_z3.

Week order annealed for prefix spread (numpy cost, same objective as schedlib.order_weeks:
sum of squared prefix spreads), positions by positions.assign, output by schedlib.write.
Usage: python3 finish.py main|vacant|x2|oil N [design-file]
"""
import sys, json, random, math, itertools
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
OUT = HERE.parents[1]
sys.path.insert(0, str(HERE.parents[2] / "tools"))
from positions import assign
import schedlib
from schedlib import write, stats, second_round

POSN = {4: "left lane 1st, right lane 1st, left lane 2nd, right lane 2nd"}


def inc_matrix(W, v, real):
    idx = {c: n for n, c in enumerate(itertools.combinations(sorted(real), 2))}
    A = np.zeros((len(W), len(idx)), dtype=np.int16)
    for w, wk in enumerate(W):
        for g in wk:
            for a, b in itertools.combinations(sorted(g), 2):
                if (a, b) in idx: A[w, idx[(a, b)]] += 1
    return A


def spreads_np(A, order, start=None):
    C = np.cumsum(A[order], axis=0)
    if start is not None: C = C + start
    return C.max(axis=1) - C.min(axis=1)


def order_blocks(W, v, real, blocks, rng, steps=20000, start=None):
    """Anneal week order (weeks only move inside their block; blocks may be permuted)."""
    A = inc_matrix(W, v, real)
    bl = []; i = 0
    for b in blocks: bl.append(list(range(i, i + b))); i += b
    def flat(bl): return [w for b in bl for w in b]
    def cost(bl):
        s = spreads_np(A, flat(bl), start)
        return int(s[:-1].max()) * 1000 + int((s.astype(np.int64) ** 2).sum())
    cur = cost(bl); best = (cur, [list(b) for b in bl]); T = 30.0
    for it in range(steps):
        nb = [list(b) for b in bl]
        if len(nb) > 1 and rng.random() < 0.15:
            i, j = rng.sample(range(len(nb)), 2); nb[i], nb[j] = nb[j], nb[i]
        else:
            cands = [x for x in nb if len(x) > 1]; b = rng.choice(cands)
            i, j = rng.sample(range(len(b)), 2); b[i], b[j] = b[j], b[i]
        n = cost(nb)
        if n <= cur or rng.random() < math.exp((cur - n) / T):
            bl, cur = nb, n
            if cur < best[0]: best = (cur, [list(b) for b in bl])
        T = max(0.3, T * 0.9996)
    return [W[w] for w in flat(best[1])], [len(b) for b in best[1]]


def load_weeks(path, r=None):
    """zsym output: first lines are weeks of 4m point ids (0-based); lanes_z3 output: JSON."""
    txt = Path(path).read_text()
    if txt.lstrip().startswith("{"):
        d = json.loads(txt); W = d["weeks"]; meta = {k: d[k] for k in ("base", "tr", "half")}
        return [[[p + 1 for p in g] for g in wk] for wk in W], meta
    lines = [l for l in txt.splitlines() if l.strip()]
    W = []; meta = {}
    for l in lines:
        if l[0].isdigit():
            p = list(map(int, l.split())); W.append([[x + 1 for x in p[i:i + 4]] for i in range(0, len(p), 4)])
        else:
            key, _, rest = l.partition(" "); meta[key.lower()] = rest.strip()
    return W, meta


def block_repeats(W, blocks):
    tot = 0; i = 0
    for b in blocks:
        c = {}
        for wk in W[i:i + b]:
            for g in wk:
                for pr in itertools.combinations(sorted(g), 2): c[pr] = c.get(pr, 0) + 1
        tot += sum(n - 1 for n in c.values()); i += b
    return tot


def header_main(v, r, lam, st, rounds=1):
    n = v // 4; lo, hi = r // n, -(-r // n)
    pc = sorted(set(tuple(sorted(x, reverse=True)) for x in st["position_counts"].values()))
    lanes = "exact" if st["lane_off"] == 0 else f"{st['lane_off']} bowler(s) off"
    h = (f"# {v} players, 4 per lane pair, {r} weeks{' (two rounds)' if rounds == 2 else ''}: every couple meets exactly {lam * rounds} times;\n" +
         (f"# every bowler on every lane pair {lo} or {hi} times (exact); positions {'/'.join(map(str, pc[-1]))}.\n" if st["lane_off"] == 0 else
          f"# lane pairs NOT exact: target {lo} or {hi} times each; {st['lane_off']} bowler(s) have a lane pair outside that "
          f"(counts {min(min(x) for x in st['lane_counts'].values())}..{max(max(x) for x in st['lane_counts'].values())}); positions {'/'.join(map(str, pc[-1]))}.\n"))
    return h


def finish_main(N, path, method, seed=1, steps=20000):
    rng = random.Random(seed)
    W, meta = load_weeks(path)
    v = 4 * len(W[0]); assert v == N
    real = list(range(1, v + 1))
    W, _ = order_blocks(W, v, real, [len(W)], rng, steps)
    W = assign(W, 4)
    st = stats(W, v, 4)
    lam = st["meet"][0]
    st = write(str(OUT), f"v{N}", W, v, 4, 1, method, header_main(v, len(W), lam, st))
    d = json.load(open(OUT / f"v{N}.json"))
    d["notes"] = "design (0-based points m*class+i): " + json.dumps(meta)
    json.dump(d, open(OUT / f"v{N}.json", "w"), indent=1)
    print(f"v{N}: lanes off {st['lane_off']}, worst prefix {max(st['prefix_spread'][:-1])}, meet {st['meet']}")
    return W


if __name__ == "__main__":
    pass


def finish_vacant_rot(N, basefile, seed=1, steps=40000):
    rng = random.Random(seed); v = N; q = v - 1
    b = list(map(int, Path(basefile).read_text().split()))
    G = [b[i:i + 4] for i in range(0, v, 4)]
    G.sort(key=lambda g: q not in g)                     # inf group on lane pair 1
    W = [[[v if x == q else (x + k) % q + 1 for x in g] for g in G] for k in range(q)]
    real = list(range(1, v))
    W, _ = order_blocks(W, v, real, [len(W)], rng, steps)
    W = assign(W, 4)
    st = stats(W, v, 4, vacant=v); lam = st["meet"][0]
    method = (f"1-rotational Z_{q}+{{inf}}: base week found by simulated annealing on difference counts "
              f"(ext40/rot1.c), developed mod {q}; base group j fixed on lane pair j, so the {q} real bowlers are exactly "
              f"lane-balanced; player {v} = inf = vacant slot (that group plays three-handed, always on the first lane pair); "
              "week order annealed for prefix spread; positions by equitable edge-colouring.")
    hdr = (f"# {q} bowlers (player {v} = vacant slot), 4-per-pair groups, {q} weeks: every couple meets {lam} times;\n"
           f"# every real bowler on every lane pair {q // (v // 4)} or {-(-q // (v // 4))} times (exact). The vacancy's group is always on the first lane pair.\n")
    st = write(str(OUT), f"v{N}_vacant", W, v, 4, 1, method, hdr, vacant=v)
    d = json.load(open(OUT / f"v{N}_vacant.json")); d["notes"] = f"base week (0-based, {q} = inf): {json.dumps(G)}"
    json.dump(d, open(OUT / f"v{N}_vacant.json", "w"), indent=1)
    print(f"v{N}_vacant: lanes off {st['lane_off']}, worst prefix {max(st['prefix_spread'][:-1])}, meet {st['meet']}")


def finish_x2(N, seed=1, tries=4000, oil=False):
    rng = random.Random(seed); v = N
    d1 = json.load(open(OUT / f"v{N}.json")); W1 = schedlib.groups(d1["weeks"], 4); r = len(W1)
    best = second_round(W1, v, 4, rng, tries)
    if best is None: print("no second round found"); return
    rep, W2 = best
    W = assign(W1 + W2, 4)
    st = stats(W, v, 4); lam = st["meet"][0]
    method = (f"Round 1 = v{N} (same groups and lane pairs); round 2 = round 1 under a random lane-pair permutation and a "
              "bowler relabelling by randomised bipartite matching so every bowler's lane totals over both rounds are floor/ceil "
              f"(schedlib.second_round, best of {tries} tries for fewest round-1 groups recurring: {rep}). "
              f"Positions equitable over all {2 * r} weeks.")
    hdr = header_main(v, 2 * r, lam // 2, st, rounds=2)
    if oil: hdr += f"# Oil-pattern blocks (weeks): [{r}, {r}] -- no couple meets twice on the same pattern.\n"
    st = write(str(OUT), f"v{N}_x2", W, v, 4, 2, method, hdr)
    d = json.load(open(OUT / f"v{N}_x2.json")); d["repeated_groups"] = rep; d["cycle_weeks"] = r
    if oil: d["oil_blocks"] = [r, r]
    json.dump(d, open(OUT / f"v{N}_x2.json", "w"), indent=1)
    print(f"v{N}_x2: lanes off {st['lane_off']}, repeated groups {rep}, worst prefix {max(st['prefix_spread'][:-1])}, meet {st['meet']}")


def finish_oil(N, path, method, seed=1, steps=40000):
    """Weeks of a lane-exact design split into the fewest clash-free blocks (exact colouring of the
    week clash graph, oilcolor.py); blocks = colour classes, block and week order annealed."""
    from oilcolor import clash_graph, colour
    rng = random.Random(seed)
    W, meta = load_weeks(path); v = 4 * len(W[0]); real = list(range(1, v + 1))
    adj = clash_graph(W)
    for k in range(4, 40):
        col, r = colour(adj, k)
        if r: break
    classes = [[w for w in range(len(W)) if col[w] == c] for c in range(k)]
    W0 = [W[w] for cl in classes for w in cl]
    W1, blocks = order_blocks(W0, v, real, [len(c) for c in classes], rng, steps)
    W1 = assign(W1, 4)
    rp = block_repeats(W1, blocks); st = stats(W1, v, 4); lam = st["meet"][0]
    hdr = f"# {v} players, 4 per lane pair, {len(W1)} weeks: every couple meets exactly {lam} times.\n"
    hdr += f"# Oil-pattern blocks (consecutive weeks): {' + '.join(map(str, blocks))} = {len(W1)} weeks.\n"
    i = 1
    for n_, b in enumerate(blocks): hdr += f"#   block {n_ + 1}: weeks {i}-{i + b - 1}\n"; i += b
    hdr += f"# Same-block repeat meetings: {rp}" + (f" (no couple meets twice on one pattern; every couple meets on {lam} different patterns)" if rp == 0 else "") + ".\n"
    hdr += f"# Lane pairs: {'exact (floor/ceil for every bowler)' if st['lane_off'] == 0 else str(st['lane_off']) + ' bowler(s) off'}.\n"
    st = write(str(OUT), f"v{N}_oil", W1, v, 4, 1, method, hdr)
    d = json.load(open(OUT / f"v{N}_oil.json")); d["blocks"] = blocks; d["block_repeats"] = rp
    d["notes"] = "design (0-based points m*class+i): " + json.dumps(meta)
    json.dump(d, open(OUT / f"v{N}_oil.json", "w"), indent=1)
    print(f"v{N}_oil: blocks {blocks} repeats {rp} lanes off {st['lane_off']} worst prefix {max(st['prefix_spread'][:-1])}")
