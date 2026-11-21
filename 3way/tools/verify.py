#!/usr/bin/env python3
"""Independent checker for schedules/3way/v*.json and the matching .toml files.

File kinds: v{N}.json (one cycle), v{N}_x2.json (two cycles, "cycles": 2) and
v{N}_vacant.json (player "vacant" is an empty slot; judged on real bowlers).

Checks per file:
  * each week is a permutation of 1..v,
  * every couple of real bowlers meets exactly cycles*lambda times,
  * lane counts recomputed == stored, and whether each real bowler is on each lane
    pair floor/ceil(r/n) times (reported; must match lane_balance_exact),
  * prefix spreads recomputed == stored,
  * position counts recomputed == stored and floor/ceil(r/3) for every real bowler
    (a hard requirement), position prefix spreads == stored,
  * TOML weeks == JSON weeks,
  * single-cycle files: the stored second-cycle relabelling, rebuilt and checked
    across the join (pair counts reach 2*lambda, join spread, lane totals).
"""
import json
import re
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent


def floor_ceil_off(counts, total, parts):
    lo, hi = total // parts, -(-total // parts)
    return lo, hi, sum(1 for c in counts for x in c if not lo <= x <= hi)


def check(path):
    d = json.loads(path.read_text())
    v, weeks, lam = d["players"], d["weeks"], d["lambda"]
    assert d["group"] == 3
    cycles = d.get("cycles", 1)
    vac = d.get("vacant")
    real = [p for p in range(1, v + 1) if p != vac]
    r, nl = len(weeks), v // 3
    errs, notes = [], []
    for i, w in enumerate(weeks):
        if sorted(w) != list(range(1, v + 1)):
            errs.append(f"week {i+1} not a permutation")
    if r != cycles * lam * (v - 1) // 2:
        errs.append(f"{r} weeks, expected {cycles * lam * (v - 1) // 2}")
    groups = [[w[k:k + 3] for k in range(0, v, 3)] for w in weeks]

    meet = {pr: 0 for pr in combinations(real, 2)}
    spreads = []
    for wk in groups:
        for g in wk:
            for a, b in combinations(sorted(g), 2):
                if (a, b) in meet:
                    meet[(a, b)] += 1
        spreads.append(max(meet.values()) - min(meet.values()))
    nbad = sum(1 for c in meet.values() if c != cycles * lam)
    if nbad:
        errs.append(f"{nbad} couples do not meet {cycles * lam} times")
    if spreads != d["prefix_spread"]:
        errs.append("prefix_spread mismatch")

    lane = {p: [0] * nl for p in range(1, v + 1)}
    pos = {p: [0, 0, 0] for p in range(1, v + 1)}
    pos_pref = []
    for wk in groups:
        for l, g in enumerate(wk):
            for k, p in enumerate(g):
                lane[p][l] += 1
                pos[p][k] += 1
        pos_pref.append(max(max(pos[p]) - min(pos[p]) for p in real))
    if {str(p): c for p, c in lane.items()} != d["lane_counts"]:
        errs.append("lane_counts mismatch")
    lo, hi, lane_off = floor_ceil_off([lane[p] for p in real], r, nl)
    if d["lane_balance_exact"] != (lane_off == 0):
        errs.append("lane_balance_exact flag wrong")
    if lane_off:
        notes.append(f"lane balance NOT exact: {lane_off} bowler-lane cell(s) outside [{lo},{hi}]")
    if {str(p): c for p, c in pos.items()} != d["position_counts"]:
        errs.append("position_counts mismatch")
    plo, phi, pos_off = floor_ceil_off([pos[p] for p in real], r, 3)
    if pos_off:
        errs.append(f"position balance off in {pos_off} cells")
    if d["position_prefix_spread"] != pos_pref:
        errs.append("position_prefix_spread mismatch")

    extra = []
    if vac:
        vl = sorted({l + 1 for wk in groups for l, g in enumerate(wk) if vac in g})
        extra.append(f"vacancy={vac} on lane pair(s) {vl}")
    if cycles == 2:
        h = r // 2
        join = len({tuple(sorted(g)) for g in groups[h - 1]} & {tuple(sorted(g)) for g in groups[h]})
        extra.append(f"repeated groups at join={join}")
    if "second_cycle" in d:
        sc = d["second_cycle"]
        sig = {int(k): x for k, x in sc["relabel"].items()}
        lm = sc["lane_map"]
        if sorted(sig.values()) != list(range(1, v + 1)) or sorted(lm) != list(range(nl)):
            errs.append("second-cycle relabel/lane_map not permutations")
        cyc2 = []
        for wk in groups:
            nw = [None] * nl
            for l, g in enumerate(wk):
                nw[lm[l]] = [sig[p] for p in g]
            cyc2.append(nw)
        meet2, sp2 = dict(meet), []
        for wk in cyc2:
            for g in wk:
                for a, b in combinations(sorted(g), 2):
                    meet2[(a, b)] += 1
            sp2.append(max(meet2.values()) - min(meet2.values()))
        if any(c != 2 * lam for c in meet2.values()):
            errs.append("relabelled second cycle does not give 2*lambda")
        lane2 = {p: list(c) for p, c in lane.items()}
        for wk in cyc2:
            for l, g in enumerate(wk):
                for p in g:
                    lane2[p][l] += 1
        lo2, hi2, off2 = floor_ceil_off(list(lane2.values()), 2 * r, nl)
        if (off2 == 0) != (sc["two_cycle_lane_penalty"] == 0):
            errs.append("two_cycle_lane_penalty inconsistent")
        join = len({tuple(sorted(g)) for g in groups[-1]} & {tuple(sorted(g)) for g in cyc2[0]})
        extra.append(f"relabelled cycle 2: join spread={max(sp2)}, two-cycle lanes "
                     f"{'exact' if not off2 else f'{off2} cells off'}, repeated groups at join={join}")

    toml = path.with_suffix(".toml").read_text()
    tw = [[int(x) for x in m.split(",")]
          for m in re.findall(r"^\s*\[([\d,\s]+)\],?\s*$", toml, re.M)]
    if tw != weeks:
        errs.append("TOML weeks differ from JSON")

    print(f"{path.name:16s} {'OK' if not errs else 'FAIL'}  v={v} weeks={r} "
          f"lambda={lam}x{cycles} lanes[{lo},{hi}]={'exact' if not lane_off else 'off'} "
          f"positions[{plo},{phi}]={'exact' if not pos_off else 'off'} "
          f"worst_prefix_spread={max(spreads)} prefix_spread={''.join(map(str, spreads))} "
          f"max_position_prefix_spread={max(pos_pref)}")
    for e in extra:
        print("     ", e)
    for e in errs + notes:
        print("   -", e)
    return not errs


def sort_key(p):
    m = re.match(r"v(\d+)(.*)", p.stem)
    return int(m.group(1)), m.group(2)


if __name__ == "__main__":
    files = sorted((f for f in HERE.glob("v*.json") if re.match(r"v\d+", f.stem)), key=sort_key)
    ok = all([check(f) for f in files])
    print("ALL OK" if ok else "SOME FAILURES")
    sys.exit(0 if ok else 1)
