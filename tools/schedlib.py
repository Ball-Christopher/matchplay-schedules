"""Finish schedules: week order for prefix balance, positions, standard JSON/TOML,
and a two-round version built against round 1."""
import json, random, itertools, math
from collections import Counter
from positions import assign

POS = {3: "left lane 1st, right lane 1st, left lane 2nd",
       4: "left lane 1st, right lane 1st, left lane 2nd, right lane 2nd"}

def groups(flat, k):
    return [[w[i:i+k] for i in range(0, len(w), k)] for w in flat]

def meet_spreads(W, real, start=None):
    m = Counter(start or {}); out = []
    cp = list(itertools.combinations(sorted(real), 2))
    for wk in W:
        for g in wk:
            for a, b in itertools.combinations(sorted(g), 2): m[(a, b)] += 1
        v = [m[c] for c in cp]; out.append(max(v) - min(v))
    return out, m

def order_weeks(W, real, rng, steps=15000, start=None):
    o = list(range(len(W)))
    cost = lambda o: sum(s * s for s in meet_spreads([W[i] for i in o], real, start)[0])
    cur = cost(o); T = 5
    for _ in range(steps):
        i, j = rng.sample(range(len(o)), 2); o[i], o[j] = o[j], o[i]
        n = cost(o)
        if n <= cur or rng.random() < math.exp((cur - n) / T): cur = n
        else: o[i], o[j] = o[j], o[i]
        T = max(0.05, T * 0.9997)
    return [W[i] for i in o]

def stats(W, v, k, vacant=None):
    real = [p for p in range(1, v + 1) if p != vacant]; n = v // k
    lane = Counter(); pos = Counter()
    for wk in W:
        assert sorted(p for g in wk for p in g) == list(range(1, v + 1))
        for l, g in enumerate(wk):
            for q, p in enumerate(g): lane[(p, l)] += 1; pos[(p, q)] += 1
    ps, m = meet_spreads(W, real)
    lam = sorted(set(m[c] for c in itertools.combinations(real, 2)))
    r = len(W); lo, hi = r // n, -(-r // n)
    lc = {p: [lane[(p, l)] for l in range(n)] for p in real}
    return {"meet": lam, "lane_counts": lc, "position_counts": {p: [pos[(p, q)] for q in range(k)] for p in real},
            "prefix_spread": ps, "lane_off": sum(1 for p in real if any(not lo <= x <= hi for x in lc[p]))}

def write(D, name, W, v, k, rounds, method, header, vacant=None):
    st = stats(W, v, k, vacant); flat = [[p for g in wk for p in g] for wk in W]
    assert len(st["meet"]) == 1
    out = {"players": v, "group": k, "rounds": rounds, "lambda": st["meet"][0] // rounds, "weeks": flat,
           "lane_balance_exact": st["lane_off"] == 0, "lane_off_bowlers": st["lane_off"],
           "lane_counts": st["lane_counts"], "position_counts": st["position_counts"],
           "prefix_spread": st["prefix_spread"], "method": method}
    if vacant: out["vacant"] = vacant
    json.dump(out, open(f"{D}/{name}.json", "w"), indent=1)
    open(f"{D}/{name}.toml", "w").write(header + f"# Groups of {k} in lane-pair order from first_lane up; within a group: {POS[k]}.\n"
        "[schedule]\nweeks = [\n" + "".join("  " + json.dumps(w) + ",\n" for w in flat) + "]\n")
    return st

def second_round(W1, v, k, rng, tries=4000):
    """Round 2 = round 1 under a lane-pair permutation pi and a bowler relabelling
    sigma (by randomized bipartite matching) so lane totals over both rounds are
    floor/ceil; fewest groups recurring from round 1."""
    n = v // k; r = len(W1)
    c1 = Counter()
    for wk in W1:
        for l, g in enumerate(wk):
            for p in g: c1[(p, l)] += 1
    lo, hi = (2 * r) // n, -(-(2 * r) // n)
    g1 = {frozenset(g) for wk in W1 for g in wk}; best = None
    for t in range(tries):
        pi = list(range(n)); rng.shuffle(pi)
        ok = lambda p, q: all(lo <= c1[(q, pi[l])] + c1[(p, l)] <= hi for l in range(n))
        cand = {p: [q for q in range(1, v + 1) if ok(p, q)] for p in range(1, v + 1)}
        match = {}
        def aug(p, seen):
            for q in rng.sample(cand[p], len(cand[p])):
                if q in seen: continue
                seen.add(q)
                if q not in match or aug(match[q], seen):
                    match[q] = p; return True
            return False
        ps = list(range(1, v + 1)); rng.shuffle(ps)
        if not all(aug(p, set()) for p in ps): continue
        sig = {p: q for q, p in match.items()}
        W2 = [[None] * n for _ in W1]
        for w, wk in enumerate(W1):
            for l, g in enumerate(wk): W2[w][pi[l]] = [sig[p] for p in g]
        rep = sum(1 for wk in W2 for g in wk if frozenset(g) in g1)
        if best is None or rep < best[0]: best = (rep, W2)
        if rep == 0: break
    return best
