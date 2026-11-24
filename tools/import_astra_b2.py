#!/usr/bin/env python3
"""Import the library improvements from Astra's second batch (contrib/astra-2026-11-24b).

- 4way/v36_oil: Astra's four-pattern round (9+9+9+8), replacing the 11-pattern file.
- 4way/v36_oil_x2: built here; round 2 = the new oil round under a bowler relabelling
  and lane-pair permutation chosen so lanes and positions stay floor/ceil over both rounds.
- Two-round files with round 1 fixed (Astra): v{N}_x2 replaced where Astra's has fewer
  oil-pattern blocks (3way 24, 30, 36; 4way 24, 36), and new v{N}_oil_x2 files
  (3way 24, 30, 36; 4way 24, 32).
Each imported round 1 is asserted identical to the library's one-round file.
Usage: python3 tools/import_astra_b2.py
"""
import json, random, sys
from collections import Counter
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "contrib" / "astra-2026-11-24b"
sys.path.insert(0, str(ROOT / "tools"))
import schedlib  # noqa: E402

POS = {3: "left lane 1st, right lane 1st, left lane 2nd",
       4: "left lane 1st, right lane 1st, left lane 2nd, right lane 2nd"}
CREDIT = "Found by Astra (another AI agent), 24 Nov 2026; checked independently in contrib/astra-2026-11-24b."


def grp(flat, k):
    return [flat[i:i + k] for i in range(0, len(flat), k)]


def greedy(W, k):
    out, used, n = [], set(), 0
    for w in W:
        ps = {frozenset(p) for g in grp(w, k) for p in combinations(g, 2)}
        if used & ps:
            out.append(n); used, n = set(), 0
        used |= ps; n += 1
    return out + [n]


def block_lines(blocks):
    s, out = 1, []
    for i, b in enumerate(blocks, 1):
        out.append(f"#   block {i}: weeks {s}-{s + b - 1}"); s += b
    return out


def write(folder, name, flat, k, rounds, method, extra_header, blocks, round1=None):
    v = len(flat[0]); W = [grp(w, k) for w in flat]
    st = schedlib.stats(W, v, k)
    lam = st["meet"][0]
    head = [f"# {v} players, {k} per lane pair, {len(flat)} weeks"
            + (f" (two rounds): every couple meets exactly {lam} times ({lam // 2} per round)." if rounds == 2
               else f": every couple meets exactly {lam} times.")]
    if round1:
        head.append(f"# Weeks 1-{len(flat) // 2} are {round1} unchanged.")
    head.append(f"# Oil-pattern blocks (consecutive weeks): {' + '.join(map(str, blocks))} = {len(flat)} weeks.")
    head += block_lines(blocks)
    head.append(f"# Lane pairs: {'exact' if st['lane_off'] == 0 else 'NOT exact'} (floor/ceil for every bowler); positions balanced. "
                f"Worst prefix spread {max(st['prefix_spread'])}.")
    head += [f"# {line}" for line in extra_header]
    head.append(f"# Method: {method}")
    out = {"players": v, "group": k, "rounds": rounds, "lambda": lam // rounds, "weeks": flat,
           "blocks": blocks, "block_repeats": 0,
           "lane_balance_exact": st["lane_off"] == 0, "lane_off_bowlers": st["lane_off"],
           "lane_counts": st["lane_counts"], "position_counts": st["position_counts"],
           "prefix_spread": st["prefix_spread"], "method": method}
    D = ROOT / folder
    json.dump(out, open(D / f"{name}.json", "w"), indent=1)
    open(D / f"{name}.toml", "w").write(
        "\n".join(head) + f"\n# Groups of {k} in lane-pair order from first_lane up; within a group: {POS[k]}.\n"
        "[schedule]\nweeks = [\n" + "".join("  " + json.dumps(w) + ",\n" for w in flat) + "]\n")
    assert st["lane_off"] == 0, name
    print(f"{folder}/{name}: blocks {blocks} ({len(blocks)}), spread {max(st['prefix_spread'])}")


def relabel_second(W1, v, k, rng, tries=20000):
    """Round 2 = round 1 with bowler q's role taken by sigma, lane pairs permuted by pi and
    positions by tau, so that over both rounds every bowler is floor/ceil on every lane
    pair and every position. Fewest round-1 groups recurring wins."""
    n, r = v // k, len(W1)
    lane1, pos1 = Counter(), Counter()
    for w in W1:
        for l, g in enumerate(grp(w, k)):
            for q, p in enumerate(g): lane1[(p, l)] += 1; pos1[(p, q)] += 1
    lo, hi = (2 * r) // n, -(-(2 * r) // n); plo, phi = (2 * r) // k, -(-(2 * r) // k)
    g1 = {frozenset(g) for w in W1 for g in grp(w, k)}
    best = None
    for _ in range(tries):
        pi = list(range(n)); rng.shuffle(pi); tau = list(range(k)); rng.shuffle(tau)

        def ok(p, q):  # bowler p plays role q in round 2
            return (all(lo <= lane1[(p, pi[l])] + lane1[(q, l)] <= hi for l in range(n))
                    and all(plo <= pos1[(p, tau[j])] + pos1[(q, j)] <= phi for j in range(k)))
        cand = {q: [p for p in range(1, v + 1) if ok(p, q)] for q in range(1, v + 1)}
        match = {}

        def aug(q, seen):
            for p in rng.sample(cand[q], len(cand[q])):
                if p in seen: continue
                seen.add(p)
                if p not in match or aug(match[p], seen):
                    match[p] = q; return True
            return False
        qs = list(range(1, v + 1)); rng.shuffle(qs)
        if not all(aug(q, set()) for q in qs): continue
        sig = {q: p for p, q in match.items()}
        W2 = []
        for w in W1:
            gs = grp(w, k); new = [None] * n
            for l, g in enumerate(gs):
                ng = [None] * k
                for j, q in enumerate(g): ng[tau[j]] = sig[q]
                new[pi[l]] = ng
            W2.append([p for g in new for p in g])
        rep = sum(1 for w in W2 for g in grp(w, k) if frozenset(g) in g1)
        b = len(greedy(W1 + W2, k))
        key = (b, rep)
        if best is None or key < best[0]: best = (key, W2)
        if rep == 0 and b <= 8: break
    return best


def main():
    # 1. 36 in fours, four oil patterns
    a = json.load(open(SRC / "fours36_oil.json")); W = a["weeks"]
    blocks = greedy(W, 4); assert blocks == [9, 9, 9, 8]
    write("4way", "v36_oil", W, 4, 1,
          "Four layers of GF(9) = GF(3)[i]. Each Hamilton cycle of K4 on the layers gives a 9-week pattern: "
          "the base week holds the four layer zeros and, on each directed cycle edge u->v, {+-1 in u, +-(1+i) in v} and "
          "{+-i in u, +-(2+i) in v}, translated by h in GF(9). The last 8 weeks are transversal: quartets h + s_j a "
          "with s = 0, 1, 2, i for each nonzero slope a. Lanes fitted by offsets. " + CREDIT,
          ["Same-block repeat meetings: 0 (every couple meets on 3 different patterns). 4 patterns is the fewest possible: "
           "a clash-free run has at most 11 weeks and 3 x 11 < 35."], blocks)
    # 2. v36_oil_x2 (4way), built here
    best = relabel_second(W, 36, 4, random.Random(36))
    (b, rep), W2 = best
    write("4way", "v36_oil_x2", W + W2, 4, 2,
          "Round 2 = round 1 with bowlers relabelled and lane pairs and positions permuted (randomized bipartite matching), "
          "so every bowler is floor/ceil on every lane pair and every position over both rounds. "
          f"{rep} round-2 groups also occur in round 1.",
          [f"Lower bound for this round 1: 3 + ceil((8 + 35)/11) = 7 blocks."], greedy(W + W2, 4), round1="v36_oil")
    # 3. Astra two-round files, round 1 fixed
    for fn, folder, k, v, kind in [("3w24_main", "3way", 3, 24, "x2"), ("3w30_main", "3way", 3, 30, "x2"),
                                   ("3w36_main", "3way", 3, 36, "x2"), ("4w24_main", "4way", 4, 24, "x2"),
                                   ("4w36_main", "4way", 4, 36, "x2"),
                                   ("3w24_oil", "3way", 3, 24, "oil_x2"), ("3w30_oil", "3way", 3, 30, "oil_x2"),
                                   ("3w36_oil", "3way", 3, 36, "oil_x2"), ("4w24_oil", "4way", 4, 24, "oil_x2"),
                                   ("4w32_oil", "4way", 4, 32, "oil_x2")]:
        a = json.load(open(SRC / "two_rounds" / f"{fn}.json")); W = a["weeks"]
        r1name = f"v{v}" + ("_oil" if kind == "oil_x2" else "")
        R1 = json.load(open(ROOT / folder / f"{r1name}.json"))["weeks"]
        assert W[:len(R1)] == R1, fn
        blocks = greedy(W, k)
        if kind == "x2":
            old = json.load(open(ROOT / folder / f"v{v}_x2.json"))["weeks"]
            assert len(blocks) < len(greedy(old, k)), fn
        g1 = greedy(R1, k); L = (v - 1) // (k - 1)
        lb = len(g1) - 1 + -(-(g1[-1] + len(R1)) // L)
        write(folder, f"v{v}_{kind}", W, k, 2,
              "Round 1 fixed; round 2 relabelled so each bowler's less-frequent lane pair and position differ from round 1's, "
              "with a short colour class of round 2 joined to round 1's last block where possible. " + CREDIT,
              [f"Simple lower bound for this round 1: {len(g1) - 1} + ceil(({g1[-1]} + {len(R1)})/{L}) = {lb} blocks."],
              blocks, round1=r1name)


if __name__ == "__main__":
    main()
