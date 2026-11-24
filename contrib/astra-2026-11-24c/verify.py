#!/usr/bin/env python3
"""Check every schedule in 3way/ and 4way/ from its weeks alone.

For each v*.json: every week is a permutation of 1..players; every couple of
real bowlers (all but `vacant`) meets the same number of times; positions within
groups are floor/ceil for every real bowler (required); lane-pair counts are
reported as exact or not; stored lane/position counts and prefix spreads (if
present) match what the weeks give; the .toml's weeks equal the .json's.
Usage: python3 verify.py            (exit status 1 on any failure)
"""
import json, re, sys, itertools
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
bad = 0
for folder in ("3way", "4way"):
    for path in sorted((HERE / folder).glob("v*.json")):
        d = json.loads(path.read_text()); v, k, W = d["players"], d["group"], d["weeks"]
        vac = d.get("vacant"); real = [p for p in range(1, v + 1) if p != vac]
        n, r = v // k, len(W); errs = []
        if not all(sorted(w) == list(range(1, v + 1)) for w in W): errs.append("week not a permutation")
        m = Counter(); lane = Counter(); pos = Counter(); ps = []
        cp = list(itertools.combinations(real, 2))
        for w in W:
            for l in range(n):
                g = w[l * k:(l + 1) * k]
                for q, p in enumerate(g): lane[(p, l)] += 1; pos[(p, q)] += 1
                for a, b in itertools.combinations(sorted(g), 2): m[(a, b)] += 1
            vals = [m[c] for c in cp]; ps.append(max(vals) - min(vals))
        meets = sorted(set(m[c] for c in cp))
        if len(meets) != 1: errs.append(f"couples meet {meets} times")
        plo, phi = r // k, -(-r // k)
        if any(not plo <= pos[(p, q)] <= phi for p in real for q in range(k)): errs.append("positions unbalanced")
        lo, hi = r // n, -(-r // n)
        lane_off = sum(1 for p in real if any(not lo <= lane[(p, l)] <= hi for l in range(n)))
        if "lane_counts" in d and any(d["lane_counts"][str(p)] != [lane[(p, l)] for l in range(n)] for p in real):
            errs.append("stored lane_counts differ")
        if "position_counts" in d and any(d["position_counts"][str(p)] != [pos[(p, q)] for q in range(k)] for p in real):
            errs.append("stored position_counts differ")
        if "prefix_spread" in d and d["prefix_spread"] != ps: errs.append("stored prefix_spread differs")
        toml = path.with_suffix(".toml")
        if not toml.exists(): errs.append("no .toml")
        else:
            body = toml.read_text().split("weeks = [", 1)[1].rsplit("]", 1)[0]
            tw = [json.loads(x) for x in re.findall(r"\[[0-9, ]+\]", body)]
            if tw != W: errs.append(".toml weeks differ from .json")
        bad += bool(errs)
        print(f"{folder}/{path.name:15} {v:2} players{' (+vacancy)' if vac else '':11} {r:2} weeks  couples meet {meets[0] if len(meets)==1 else meets}x  "
              f"lanes {'exact' if lane_off == 0 else f'{lane_off} bowler(s) off'}  worst prefix spread {max(ps[:-1]) if r > 1 else 0}"
              + ("  FAIL: " + "; ".join(errs) if errs else ""))
print("ALL OK" if not bad else f"{bad} FAILED"); sys.exit(1 if bad else 0)
