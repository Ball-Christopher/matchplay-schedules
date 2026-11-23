"""Turn the zn/zm/oil search outputs into the library files 3way/v{30,33,36,39}*.json/.toml.

usage: python3 finish.py main N round_file      v{N}.json + v{N}_x2.json (+ v{N}_vacant for KTS sizes)
       python3 finish.py vacant N               v{N}_vacant via a 1-rotational Z_(N-1) + inf design
Search outputs: zn/zm print SOLUTION, then the weeks (bowler = n*class + x + 1, groups in lane order),
then BASE/INV lines describing the base weeks and invariant trios.
"""
import sys, json, random, itertools, math
from pathlib import Path
from collections import Counter
HERE = Path(__file__).resolve().parent
D = HERE.parents[1]                      # 3way/
sys.path.insert(0, str(HERE.parents[2] / "tools"))
from schedlib import order_weeks, stats, write, meet_spreads
from positions import assign

K = 3
LAM = {30: 2, 33: 1, 36: 2, 39: 1}

def parse(path, v):
    lines = Path(path).read_text().split("\n")
    i = lines.index("SOLUTION")
    W = []; info = []
    for ln in lines[i + 1:]:
        if not ln.strip(): continue
        if ln[0].isdigit(): W.append([int(x) for x in ln.split()])
        else: info.append(ln)
    W = [[w[j:j + K] for j in range(0, v, K)] for w in W]
    return W, info

def check_design(W, v, lam):
    m = Counter()
    for wk in W:
        assert sorted(p for g in wk for p in g) == list(range(1, v + 1))
        for g in wk:
            for a, b in itertools.combinations(sorted(g), 2): m[a, b] += 1
    assert len(m) == v * (v - 1) // 2 and set(m.values()) == {lam}, set(m.values())

def repeated_groups(W1, W2):
    g1 = {frozenset(g) for wk in W1 for g in wk}
    return sum(1 for wk in W2 for g in wk if frozenset(g) in g1)

def header(v, lam, rounds, exact, extra=""):
    two = "two rounds, " if rounds == 2 else ""
    return (f"# {v} players, 3 per lane pair, {two}every couple meets {lam * rounds} time(s);\n"
            f"# lane pairs {'exact' if exact else 'not exact'}; positions balanced.\n") + extra

def finalize_json(name, extra):
    p = D / f"{name}.json"; d = json.loads(p.read_text()); d.update(extra)
    p.write_text(json.dumps(d, indent=1))

def add_toml_line(name, line):
    p = D / f"{name}.toml"; s = p.read_text()
    s = s.replace("[schedule]\n", line + "\n[schedule]\n", 1); p.write_text(s)

def prefix_order(W, real, seed, steps, start=None):
    rng = random.Random(seed)
    best = None
    for rep in range(3):
        o = order_weeks(W, real, rng, steps=steps, start=start)
        ps = meet_spreads(o, real, start)[0]
        key = (max(ps[:-1]) if len(ps) > 1 else 0, sum(s * s for s in ps))
        if best is None or key < best[0]: best = (key, o)
    return best[1]

def method_text(v, n, cls, info, rounds):
    lam = LAM[v]
    base = " | ".join(info)
    if cls == 3:
        pts = f"Z_{n} x {{a,b,c}} (bowler = {n}*class + x + 1)"
        inv = "orbit of one transversal trio {a_j, b_(u+j), c_(w+j)} on lane l0+j"
    else:
        m = n // (cls // 3)
        pts = f"Z_{m} x {cls} classes (bowler = {m}*class + x + 1), lane pairs as {cls // 3} tracks of {m}"
        inv = "two transversal-trio orbits on a partition of the classes, each on its own track"
    kind = "Kirkman triple system KTS" if lam == 1 else "resolvable 2-(v,3,2) design"
    s = (f"{kind}({v}) on {pts}; the automorphism x -> x+1 also rotates the lane pairs (group on lane l moves to l+1). "
         f"Each round = base week(s) developed mod {n if cls == 3 else n // (cls // 3)} + invariant weeks ({inv}). "
         "Base weeks by simulated annealing on pair-orbit counts (every pure/mixed difference exactly lambda times), "
         "lanes by DFS on (lane - x) residues per class, so every bowler is on every lane pair floor/ceil(r/n) times. "
         "No trio recurs" + (" within or across the two rounds" if rounds == 2 else "") + ". Code: 3way/tools/ext40/ (zn.c / zm.c). "
         "Week order annealed for prefix balance; positions by de Werra edge colouring. Design data: " + base)
    return s

def main_files(v, path, cls=3, seed=1):
    lam = LAM[v]; n = v // 3; real = list(range(1, v + 1))
    W, info = parse(path, v)
    r = len(W) // 2 if len(W) > lam * (v - 1) // 2 else len(W)
    R1, R2 = W[:r], W[r:]
    check_design(R1, v, lam)
    steps = 4000 if v <= 33 else 3000
    R1 = prefix_order(R1, real, seed, steps)
    meth = method_text(v, n, cls, info, 1)
    R1p = assign(R1, K)
    st = write(D, f"v{v}", R1p, v, K, 1, meth, header(v, lam, 1, True))
    print(f"v{v}: lane_off {st['lane_off']} worst prefix {max(st['prefix_spread'][:-1])}")
    if R2:
        check_design(R2, v, lam)
        _, m1 = meet_spreads(R1, real)
        R2o = prefix_order(R2, real, seed + 1, steps, start=m1)
        X = assign(R1 + R2o, K)
        meth2 = method_text(v, n, cls, info, 2) + (" v{v}.json is round 1 of this pair; round 2 = a second design found with it "
            "(disjoint trio orbits, lanes exact over both rounds). Positions equitable over both rounds.").format(v=v)
        st2 = write(D, f"v{v}_x2", X, v, K, 2, meth2, header(v, lam, 2, True))
        rep = repeated_groups(R1, R2o)
        print(f"v{v}_x2: lane_off {st2['lane_off']} worst prefix {max(st2['prefix_spread'][:-1])} repeated groups {rep}")
        if lam == 1:
            finalize_json(f"v{v}_x2", {"oil_blocks": [r, r]})
            add_toml_line(f"v{v}_x2", f"# Oil-pattern blocks (weeks): [{r}, {r}] -- no couple meets twice on the same pattern.")
    elif lam == 2:
        from schedlib import second_round
        rng = random.Random(seed); best = None
        for att in range(20):
            rep, W2 = second_round(R1, v, K, rng, tries=2000)
            if best is None or rep < best[0]: best = (rep, W2)
            if rep == 0: break
        rep, W2 = best
        _, m1 = meet_spreads(R1, real)
        W2 = prefix_order(W2, real, seed + 1, steps, start=m1)
        X = assign(R1 + W2, K)
        meth2 = meth + (" Round 2 = round 1 under a lane-pair permutation and a bowler relabelling (bipartite matching, "
                        "schedlib.second_round) so lane totals are floor/ceil, keeping the try with the fewest repeated trios. "
                        "Positions equitable over both rounds.")
        st2 = write(D, f"v{v}_x2", X, v, K, 2, meth2, header(v, lam, 2, st2_exact(X, v)))
        print(f"v{v}_x2: lane_off {st2['lane_off']} worst prefix {max(st2['prefix_spread'][:-1])} repeated groups {repeated_groups(R1, W2)}")
    if lam == 1:
        vacant_from_main(v, R1, meth)

def st2_exact(X, v):
    return stats(X, v, K)['lane_off'] == 0

def write_vacant(v, W, method, extra):
    vac = v; real = [p for p in range(1, v + 1) if p != vac]; n = v // K; r = len(W)
    Wp = assign(W, K)
    st = stats(Wp, v, K, vac)
    assert len(st["meet"]) == 1
    flat = [[p for g in wk for p in g] for wk in Wp]
    # position prefix spread: worst (max - min over positions) among real bowlers after each week
    pos = Counter(); pps = []
    for wk in Wp:
        for g in wk:
            for q, p in enumerate(g): pos[p, q] += 1
        pps.append(max(max(pos[p, q] for q in range(K)) - min(pos[p, q] for q in range(K)) for p in real))
    lo, hi = r // n, -(-r // n)
    lc = st["lane_counts"]
    pen = sum(max(0, lo - x) + max(0, x - hi) for p in real for x in lc[p])
    vl = Counter(l for wk in Wp for l, g in enumerate(wk) if vac in g)
    lc_out = {str(p): lc[p] for p in real}; lc_out[str(vac)] = [vl[l] for l in range(n)]
    pc_out = {str(p): st["position_counts"][p] for p in real}
    ps = st["prefix_spread"]
    out = {"players": v, "group": K, "weeks": flat, "lambda": st["meet"][0], "lane_counts": lc_out,
           "lane_balance_exact": st["lane_off"] == 0, "lane_penalty": pen, "prefix_spread": ps,
           "worst_prefix_spread": max(ps[:-1]), "prefix_weeks_with_spread_2": [i + 1 for i, s in enumerate(ps) if s == 2],
           "position_order": "[left lane 1st, right lane 1st, left lane 2nd]", "position_counts": pc_out,
           "position_prefix_spread": pps, "vacant": vac}
    out.update(extra)
    out.update({"method": method, "finite_lane_balance_exact": st["lane_off"] == 0,
                "note": f"lane_counts, positions, lambda and prefix spreads are judged on the {v - 1} real bowlers; player {v} is the empty slot"})
    (D / f"v{v}_vacant.json").write_text(json.dumps(out, indent=1))
    (D / f"v{v}_vacant.toml").write_text("[schedule]\nweeks = [\n" + "".join("  " + json.dumps(w) + ",\n" for w in flat) + "]\n")
    print(f"v{v}_vacant: lane_off {st['lane_off']} worst prefix {max(ps[:-1])} short group lanes {dict(vl)}")

def vacant_from_main(v, R1, meth):
    m = ("The exactly lane-balanced KTS of v{v}.json with player {v} as the empty slot: every bowler, the slot included, is on every "
         "lane pair floor/ceil(r/n) times, so the real bowlers are exact and the short group moves around the lane pairs. "
         "Positions re-coloured with the vacancy treated as a player. ").format(v=v) + "Design: " + meth
    write_vacant(v, R1, m, {})

def onerot_base(v, seed):
    """Base week of a 1-rotational resolvable 2-(v,3,2) design over Z_(v-1) + inf by annealing."""
    q = v - 1; rng = random.Random(seed); H = q // 2
    def dif(a, b): d = (a - b) % q; return min(d, q - d)
    while True:
        pts = list(range(q)); rng.shuffle(pts)
        G = [["inf"] + pts[:2]] + [pts[2 + 3 * i: 5 + 3 * i] for i in range(v // 3 - 1)]
        def cost():
            c = Counter()
            for g in G:
                f = [x for x in g if x != "inf"]
                for a, b in itertools.combinations(f, 2): c[dif(a, b)] += 1
            return sum(abs(c[d] - 2) for d in range(1, H + 1))
        cur = cost(); T = 1.0
        for it in range(200000):
            if cur == 0: break
            i, j = rng.sample(range(len(G)), 2)
            a, b = rng.randrange(len(G[i])), rng.randrange(len(G[j]))
            if G[i][a] == "inf" or G[j][b] == "inf": continue
            G[i][a], G[j][b] = G[j][b], G[i][a]
            c = cost()
            if c <= cur or rng.random() < math.exp((cur - c) / T): cur = c
            else: G[i][a], G[j][b] = G[j][b], G[i][a]
            T = max(0.15, T * 0.9999)
        if cur: continue
        # no repeated trios: base triples pairwise non-translates
        canon = lambda g: min(tuple(sorted((x + s) % q for x in g)) for s in range(q))
        cs = [canon(g) for g in G[1:]]
        if len(set(cs)) == len(cs): return G

def vacant_onerot(v, seed=1):
    q = v - 1; G = onerot_base(v, seed); real = list(range(1, v))
    lab = lambda x: v if x == "inf" else x + 1
    W = [[[lab(x if x == "inf" else (x + i) % q) for x in g] for g in G] for i in range(q)]
    check_design(W, v, 2)
    W = prefix_order(W, real, seed, 3000)
    m = (f"1-rotational resolvable 2-(v,3,2) design over Z_{q} + inf, inf = vacancy (player {v}); base block j kept on lane pair j "
         "in every developed week, so each real bowler meets each base point once and lands on each lane pair floor/ceil(r/n) times; "
         "the short group is always on lane pair(s) [1]; week order annealed for prefix spread; positions coloured with the vacancy "
         "treated as a player. Base week by annealing on differences (each of 1..%d twice), no base triple a translate of another. "
         "Code: 3way/tools/ext40/finish.py" % (q // 2))
    write_vacant(v, W, m, {"base_class": [[x for x in g] for g in G]})

if __name__ == "__main__":
    what, v = sys.argv[1], int(sys.argv[2])
    if what == "main": main_files(v, sys.argv[3], cls=int(sys.argv[4]) if len(sys.argv) > 4 else 3)
    elif what == "vacant": vacant_onerot(v, int(sys.argv[3]) if len(sys.argv) > 3 else 1)

def oil_file(v, path, seed=1):
    """v{N}_oil from a zo output: lines 'W<block> <week>' then BASE/INV lines."""
    lines = Path(path).read_text().split("\n"); i = lines.index("SOLUTION")
    blk = {}; info = []
    for ln in lines[i + 1:]:
        if ln.startswith("W"):
            b, *w = ln.split(); w = [int(x) for x in w]
            blk.setdefault(int(b[1:]), []).append([w[j:j + K] for j in range(0, v, K)])
        elif ln.strip(): info.append(ln)
    allw = [wk for b in blk for wk in blk[b]]
    check_design(allw, v, 2)
    for b, ws in blk.items():
        mm = Counter()
        for wk in ws:
            for g in wk:
                for a, c in itertools.combinations(sorted(g), 2): mm[a, c] += 1
        assert max(mm.values()) == 1, f"block {b} clashes"
    real = list(range(1, v + 1)); order = sorted(blk, key=lambda b: -len(blk[b]))
    rng_seed = seed; W = []; start = None
    for b in order:
        ws = prefix_order(blk[b], real, rng_seed, 2500, start=start) if len(blk[b]) > 1 else blk[b]
        W += ws; _, start = meet_spreads(W, real); rng_seed += 1
    blocks = [len(blk[b]) for b in order]
    Wp = assign(W, K); st = stats(Wp, v, K)
    assert st["lane_off"] == 0 and st["meet"] == [2]
    flat = [[p for g in wk for p in g] for wk in Wp]
    ps = st["prefix_spread"]
    if v == 36:
        meth = ("Points Z_12 x {a,b,c} (bowler = 12*class + x + 1) with automorphism x -> x+1, which also rotates the 12 lane pairs. "
                "Two base weeks P0, Q0 developed mod 12 plus 11 Z_12-invariant weeks (orbit of a transversal trio). "
                "Block 1 (16 weeks) = P0..P11 + 4 invariant weeks: every pair-orbit at most once, leaving the 3 antipodal orbits {x, x+6} "
                "and 3 mixed orbits M (a triangle of class pairs with an odd number of odd differences). "
                "Blocks 2 and 3 = Q0..Q5 + 4 invariant weeks and Q6..Q11 + 3 invariant weeks: Q0 holds the antipodal pairs once "
                "(so Q_i meets Q_(i+6) only there) and each M orbit either twice at offsets 6 apart or in one invariant week of each block. "
                "v24's split (one development + 5 invariant weeks = 17) is impossible here by parity: under Z_12 -> Z_2 every trio and every "
                "transversal invariant week has an even number of odd-difference pairs, but that block would need 27 odd-difference orbits. "
                "Both parts by simulated annealing on pair-orbit counts, lanes by DFS on (lane - x) residues, exact. "
                "Biggest block first; week order within blocks annealed for prefix spread; positions by de Werra edge colouring. "
                "Code: 3way/tools/ext40/zo.c (oil36b). Design data: " + " | ".join(info))
    else:
        meth = ("Points Z_5 x 6 classes (bowler = 5*class + x + 1), lane pairs as 2 tracks of 5; x -> x+1 rotates both tracks "
                "(Z_10 x 3 is impossible for 30 by parity). Four base weeks developed mod 5 plus 9 invariant weeks (two transversal-trio orbits on "
                "a partition of the classes, one per track). Block 1 (14 weeks) = 2 base weeks + 4 invariant weeks: a Z_5-invariant nearly "
                "Kirkman system NKTS(30) leaving a 1-factor F of 3 mixed orbits. Blocks 2 (1 base + 4 invariant, 9 weeks) and 3 (1 base + 1 "
                "invariant, 6 weeks) together use every pair-orbit once and the orbits of F twice, once in each block. Both parts by simulated "
                "annealing on pair-orbit counts with a per-block penalty; lanes by DFS on (track, lane - x) residues, exact. Biggest block first; "
                "week order within blocks annealed for prefix spread; positions by de Werra edge colouring. Code: 3way/tools/ext40/zo.c (oil30b). "
                "Design data: " + " | ".join(info))
    out = {"players": v, "group": K, "rounds": 1, "lambda": 2, "weeks": flat, "blocks": blocks,
           "lane_balance_exact": True, "method": meth}
    (D / f"v{v}_oil.json").write_text(json.dumps(out))
    cum = 0; parts = []
    for i, b in enumerate(blocks): parts.append(f"block {i + 1} = weeks {cum + 1}-{cum + b}"); cum += b
    L = [f"# {v} bowlers, groups of 3, {len(flat)} weeks, every couple meets exactly twice.",
         f"# Oil-pattern blocks (weeks, in order): {blocks} -- " + ", ".join(parts) + ".",
         "# Within a block no couple shares a group twice, so each couple meets on 2 different patterns.",
         f"# Lane pairs = consecutive groups of 3 in each week; lane balance exact: true. Worst prefix spread {max(ps[:-1])}.",
         "# Method: " + meth, "[schedule]", "weeks = ["] + ["  " + json.dumps(w) + "," for w in flat] + ["]"]
    (D / f"v{v}_oil.toml").write_text("\n".join(L) + "\n")
    print(f"v{v}_oil: blocks {blocks} worst prefix {max(ps[:-1])} prefix {ps}")

if __name__ == "__main__" and sys.argv[1] == "oil":
    oil_file(int(sys.argv[2]), sys.argv[3])
