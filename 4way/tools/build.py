#!/usr/bin/env python3
"""Step 3: assemble final schedules -> v{N}.json/.toml and v{N}_x2.json/.toml.

Inputs per roster (weeks already ordered, groups already in lane-pair order):
  16: designs_raw.json AG(2,4) + lanes16_out.json      (lanes16.py)
  12: sat_v12_*.json (prefix-spread-2 design) + lanes.balance_lanes_opt
  24: best of anneal / cyclic sweep, + lanes.balance_lanes
  28: designs_raw.json cyclic design + lanes.balance_lanes (exact)
Cycle 2 = same groups, same week order; its lane-pair order is re-solved by
lanes.balance_lanes_next so the two cycles together are lane balanced (falls back
to the best cyclic lane shift if that is infeasible).
Positions inside each group: positions.assign_positions over the TWO-cycle sequence,
so cycle 1 alone and both cycles together are position-balanced.
"""
import json, sys
from itertools import combinations
import lanes as L, positions as P

def pair_prefix_spread(v, weeks, skip=None):
    idx = {p: i for i, p in enumerate(combinations([x for x in range(1, v + 1) if x != skip], 2))}
    c = [0] * len(idx); out = []
    for wk in weeks:
        for G in wk:
            for a, b in combinations(sorted(x for x in G if x != skip), 2):
                c[idx[(a, b)]] += 1
        out.append(max(c) - min(c))
    return out

def lane_spread(cnt):
    return max(max(c) - min(c) for c in cnt.values())

def best_shift(weeks):
    n = len(weeks[0]); best = None
    for k in range(n):
        two = weeks + [[wk[(l - k) % n] for l in range(n)] for wk in weeks]
        c = L.lane_counts(two)
        score = (lane_spread(c), sum(max(x) - min(x) for x in c.values()))
        if best is None or score < best[0]:
            best = (score, k)
    return best[1]

def relabel_cycle(weeks):
    """Cycle 2 = cycle 1 with bowlers relabelled by pi and lane pairs permuted by
    sigma. Any relabelling keeps the pair design, so the join keeps the same prefix
    spreads (all couples sit at lambda after cycle 1). Choose pi by bipartite
    matching so that bowler q's two-cycle lane counts c1[q] + sigma(c1[pi^-1 q])
    are all in the floor/ceil band for 2r weeks. Returns (weeks2, desc) or None."""
    from itertools import permutations
    n = len(weeks[0]); r = len(weeks)
    c1 = L.lane_counts(weeks)
    LO, HI = (2 * r) // n, -(-(2 * r) // n)
    players = sorted(c1)
    sigmas = list(permutations(range(n))) if n <= 5 else [tuple((l + k) % n for l in range(n)) for k in range(n)]
    for sg in sigmas:
        # c2 for bowler q if q takes the role of s: lane sg[l] gets c1[s][l]
        def ok(q, s):
            c2 = [0] * n
            for l in range(n):
                c2[sg[l]] = c1[s][l]
            return all(LO <= c1[q][l] + c2[l] <= HI for l in range(n))
        adj = {q: [s for s in players if ok(q, s)] for q in players}
        match = {}  # s -> q
        def aug(q, seen):
            for s in adj[q]:
                if s in seen: continue
                seen.add(s)
                if s not in match or aug(match[s], seen):
                    match[s] = q; return True
            return False
        if all(aug(q, set()) for q in players):
            pi = {s: q for s, q in match.items()}  # bowler s of cycle 1 -> label q in cycle 2
            w2 = []
            for wk in weeks:
                row = [None] * n
                for l, G in enumerate(wk):
                    row[sg[l]] = [pi[p] for p in G]
                w2.append(row)
            return w2, {"relabel": {str(s): q for s, q in sorted(pi.items())}, "lane_map": list(sg)}
    return None

def emit(v, lam, weeks, method, notes):
    n = v // 4; r = len(weeks)
    rel = relabel_cycle(weeks)
    if rel:
        cyc2, info = rel
        rule = ("cycle 2 = cycle 1 with bowler b renamed relabel[b] and lane pair g moved to lane_map[g] "
                "(still a resolvable design, so the join keeps the cycle-1 prefix spreads; lane counts balanced over both cycles)")
    else:
        info = {}
        cyc2, st = L.balance_lanes_next(weeks, L.lane_counts(weeks), 300)
    if rel:
        pass
    elif cyc2 is None:
        k = best_shift(weeks)
        cyc2 = [[wk[(l - k) % n] for l in range(n)] for wk in weeks]
        rule = f"repeat the same weeks in the same order with lane pair g -> (g+{k}) mod {n}"
    else:
        rule = "repeat the same weeks in the same order; lane-pair order re-solved (z3) so both cycles together are lane balanced"
    both = P.assign_positions(weeks + cyc2)
    w1, w2 = both[:r], both[r:]
    d = record(v, lam, w1, method, notes)
    json.dump(d, open(f"v{v}.json", "w"), indent=1)
    write_toml(f"v{v}.toml", w1, f"{v} bowlers, 4-way, {r} weeks = one cycle (lambda={lam}). "
               f"Chunks of 4 = lane pairs 1..{n}; order in chunk = [L1st, R1st, L2nd, R2nd].")
    d2 = record(v, 2 * lam, w1 + w2, method + " Double round: second cycle as in 'second_cycle_rule'.", notes)
    d2["cycle_weeks"] = r
    d2["second_cycle_rule"] = rule + "; positions coloured over both cycles together, so cycle 1 is identical to v%d.json" % v
    d2.update(info)
    json.dump(d2, open(f"v{v}_x2.json", "w"), indent=1)
    write_toml(f"v{v}_x2.toml", w1 + w2, f"{v} bowlers, 4-way, {2*r} weeks = two cycles (lambda={2*lam}); "
               f"weeks 1-{r} = v{v}.toml, weeks {r+1}-{2*r} = relabelled cycle (see v{v}_x2.json).")
    for tag, dd in (("", d), ("_x2", d2)):
        print(f"v{v}{tag}", "weeks", len(dd["weeks"]), "lane exact", dd["lane_balance_exact"],
              "pair prefix", dd["prefix_spread"], "pos prefix max", max(dd["prefix_position_spread"]))

flat = lambda ws: [[p for G in wk for p in G] for wk in ws]

def record(v, lam, ws, method, notes, vacant=None):
    n = v // 4; r = len(ws)
    lc = L.lane_counts(ws); pc = P.position_counts(ws)
    lo, hi = r // n, -(-r // n)
    real = [p for p in sorted(lc) if p != vacant]
    exact_lane = all(lo <= x <= hi for p in real for x in lc[p])
    d = {"players": v, "group": 4, "weeks": flat(ws), "lambda": lam}
    if vacant:
        d["vacant"] = vacant
    d.update({
        "lane_counts": {str(p): lc[p] for p in sorted(lc)},
        "position_counts": {str(p): pc[p] for p in sorted(pc)},
        "prefix_spread": pair_prefix_spread(v, ws, skip=vacant),
        "prefix_position_spread": P.prefix_position_spread(ws),
        "lane_balance_exact": exact_lane,
        "lane_off": {str(p): lc[p] for p in real if not all(lo <= x <= hi for x in lc[p])},
        "method": method, "notes": notes})
    return d

def write_toml(path, ws, title):
    lines = [f"# {title}", "[schedule]", "weeks = ["]
    lines += ["  [" + ", ".join(map(str, w)) + "]," for w in flat(ws)]
    lines.append("]")
    open(path, "w").write("\n".join(lines) + "\n")

if __name__ == "__main__":
    which = sys.argv[1:] or ["12", "16", "24", "28"]
    D = json.load(open("designs_raw.json"))
    F = json.load(open("final_inputs.json"))
    for v in which:
        e = F[v]
        emit(int(v), e["lambda"], e["weeks"], e["method"], e["notes"])
