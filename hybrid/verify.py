"""Verify hybrid single-round schedules in hybrid/files/*.json.

File format:
  {"players": v, "lane_pairs": n,
   "weeks": [ [group_or_null, ...n entries...], ... ],   # entry L = lane pair L+1
   "method": "...", ...}
A group is a list of 2, 3 or 4 roster numbers in playing order. null = lane pair empty.
Two 2-way matches sharing a lane pair ("wrapped") are written as one entry
{"wrapped": [[a,b],[c,d]]}; they count as one lane-pair visit for each bowler.

Checks: every bowler bowls once a week; every couple meets exactly once;
format-fair (every bowler has the same number of 2-, 3- and 4-way weeks);
lane-exact (every bowler on every lane pair floor(R/n) or ceil(R/n) times);
positions (per format, each bowler's position counts differ by at most 1, reported)."""
import json, sys, glob, itertools, collections, os
def groups(entry):
    if entry is None: return []
    if isinstance(entry, dict): return entry["wrapped"]
    return [entry]
def check(path):
    d = json.load(open(path)); v = d["players"]; n = d["lane_pairs"]; W = d["weeks"]; R = len(W)
    errs = []; meet = collections.Counter(); fmt = collections.defaultdict(collections.Counter)
    lane = collections.defaultdict(collections.Counter); pos = collections.defaultdict(collections.Counter)
    for t, wk in enumerate(W):
        if len(wk) != n: errs.append(f"week {t+1}: {len(wk)} lane entries, expected {n}")
        seen = []
        for L, e in enumerate(wk):
            for g in groups(e):
                if len(g) not in (2, 3, 4): errs.append(f"week {t+1}: group size {len(g)}")
                for i, p in enumerate(g):
                    seen.append(p); fmt[p][len(g)] += 1; lane[p][L] += 1; pos[(p, len(g))][i] += 1
                for a, b in itertools.combinations(sorted(g), 2): meet[(a, b)] += 1
        if sorted(seen) != list(range(1, v + 1)): errs.append(f"week {t+1}: not every bowler exactly once")
    bad = [c for c in itertools.combinations(range(1, v + 1), 2) if meet[c] != 1]
    if bad: errs.append(f"{len(bad)} couples not meeting exactly once, e.g. {bad[:3]}")
    mixes = {tuple(fmt[p][s] for s in (2, 3, 4)) for p in range(1, v + 1)}
    fair = len(mixes) == 1
    lo, hi = R // n, -(-R // n)
    lane_off = sum(1 for p in range(1, v + 1) if any(not lo <= lane[p][L] <= hi for L in range(n)))
    pos_off = sum(1 for (p, s), c in pos.items() if max(c[i] for i in range(s)) - min(c[i] for i in range(s)) > 1)
    week_kinds = collections.Counter(tuple(sorted((len(g) for e in wk for g in groups(e)), reverse=True)) for wk in W)
    return {"file": os.path.basename(path), "v": v, "weeks": R, "lane_pairs": n, "valid": not errs, "errors": errs[:5],
            "format_fair": fair, "mix_2_3_4": sorted(mixes), "lane_off_bowlers": lane_off,
            "position_off": pos_off, "week_kinds": {" ".join(map(str, k)): c for k, c in week_kinds.items()}}
if __name__ == "__main__":
    files = sys.argv[1:] or sorted(glob.glob(os.path.join(os.path.dirname(__file__) or ".", "files", "*.json")))
    ok = True
    for f in files:
        r = check(f); ok &= r["valid"]
        print(json.dumps(r))
    print("ALL VALID" if ok else "SOME INVALID")
