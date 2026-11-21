#!/usr/bin/env python3
"""Independent checker (no project imports) for every v{N}.json, v{N}_x2.json and
v{N}_vacant.json in this folder.
  - each week is a permutation of 1..v
  - every couple meets exactly `lambda` times (x2 files store 2*lambda; for vacant
    files the vacancy slot is a design point, so this holds for it too)
  - lane-pair counts recomputed, compared with the file, checked against
    floor/ceil(r/n) (real players only in vacant files)
  - position counts recomputed, compared, checked against floor/ceil(r/4)
  - prefix couple spreads recomputed and compared (real couples only if vacant)
  - for x2 files: weeks 1..cycle_weeks equal the single-round v{N}.json."""
import glob, json, os, re, sys
from itertools import combinations

def check(path):
    d = json.load(open(path)); name = os.path.basename(path)
    v, k, lam = d["players"], d["group"], d["lambda"]; W = d["weeks"]
    vac = d.get("vacant"); n = v // k; r = len(W)
    problems = []
    for i, w in enumerate(W):
        if sorted(w) != list(range(1, v + 1)):
            problems.append(f"week {i+1} not a permutation")
    meet = {pq: 0 for pq in combinations(range(1, v + 1), 2)}
    real = [p for p in range(1, v + 1) if p != vac]
    spreads = []
    for w in W:
        for s in range(0, v, k):
            for a, b in combinations(sorted(w[s:s + k]), 2):
                meet[(a, b)] += 1
        vals = [c for (a, b), c in meet.items() if a != vac and b != vac]
        spreads.append(max(vals) - min(vals))
    mv = sorted(set(meet.values()))
    if mv != [lam]:
        problems.append(f"couple meetings {mv} != {lam}")
    lane = {p: [0] * n for p in range(1, v + 1)}; pos = {p: [0] * k for p in range(1, v + 1)}
    for w in W:
        for i, p in enumerate(w):
            lane[p][i // k] += 1; pos[p][i % k] += 1
    if {str(p): c for p, c in lane.items()} != d["lane_counts"]: problems.append("lane_counts mismatch")
    if {str(p): c for p, c in pos.items()} != d["position_counts"]: problems.append("position_counts mismatch")
    if spreads != d["prefix_spread"]: problems.append("prefix_spread mismatch")
    llo, lhi = r // n, -(-r // n); plo, phi = r // k, -(-r // k)
    loff = {p: lane[p] for p in real if not all(llo <= x <= lhi for x in lane[p])}
    poff = {p: pos[p] for p in range(1, v + 1) if not all(plo <= x <= phi for x in pos[p])}
    if poff: problems.append(f"{len(poff)} bowlers outside position band")
    if bool(loff) == d.get("lane_balance_exact", not loff):
        problems.append("lane_balance_exact flag wrong")
    if "cycle_weeks" in d:
        base = os.path.join(os.path.dirname(path), f"v{v}.json")
        if os.path.exists(base) and json.load(open(base))["weeks"] != W[:d["cycle_weeks"]]:
            problems.append("first cycle differs from single-round file")
    print(f"{name}: v={v} weeks={r} lambda={lam}" + (f" vacant={vac}" if vac else ""))
    print(f"  permutations + couple meetings {mv}: {'OK' if not any('perm' in p or 'meet' in p for p in problems) else 'FAIL'}")
    print(f"  lane pairs (want {llo}-{lhi}{', real players' if vac else ''}): " +
          ("exact" if not loff else f"{len(loff)} off: " + ", ".join(f"{p}:{c}" for p, c in sorted(loff.items()))))
    print(f"  positions (want {plo}-{phi}): " + ("exact" if not poff else f"{len(poff)} off"))
    print(f"  prefix couple spread{' (real couples)' if vac else ''}: {spreads}  worst={max(spreads[:-1]) if r > 1 else 0}")
    print("  RESULT:", "PASS" if not problems else "FAIL " + "; ".join(problems))
    return not problems

here = os.path.dirname(os.path.abspath(__file__))
files = [f for f in glob.glob(os.path.join(here, "v*.json"))
         if re.fullmatch(r"v\d+(_x2|_vacant)?\.json", os.path.basename(f))]
key = lambda f: (int(re.search(r"\d+", os.path.basename(f)).group()), os.path.basename(f))
ok = all([check(f) for f in sorted(files, key=key)])
print("ALL PASS" if ok else "SOME FAILED")
sys.exit(0 if ok else 1)
