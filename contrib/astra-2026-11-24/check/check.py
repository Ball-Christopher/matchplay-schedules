import sys, itertools, collections, json
import numpy as np
sys.path.insert(0, __import__("os").path.dirname(__file__)); from parse import parse
def analyse(weeks, pattern=None):
    k = max(len(g) for g in weeks[0]); n = len(weeks[0])
    players = sorted({p for w in weeks for g in w for p in g if p})
    v = len(players); idx = {p:i for i,p in enumerate(players)}
    R = len(weeks)
    res = {'v': v, 'k': k, 'lanes': n, 'weeks': R}
    ok = True
    for w in weeks:
        flat = [p for g in w for p in g if p]
        if len(flat) != len(set(flat)) or len(flat) != v or len(w) != n: ok = False
    res['weeks_valid'] = ok
    M = np.zeros((v, v), dtype=np.int32)
    lane = np.zeros((v, n), dtype=np.int32); pos = np.zeros((v, k), dtype=np.int32)
    vac_lane = [0]*n
    spread = 0; spreadW = []
    iu = np.triu_indices(v, 1)
    for t, w in enumerate(weeks):
        for L, g in enumerate(w):
            if 0 in g: vac_lane[L] += 1
            ids = [idx[p] for p in g if p]
            for j, p in enumerate(g):
                if p: pos[idx[p], j] += 1
            for i in ids: lane[i, L] += 1
            for a, b in itertools.combinations(ids, 2):
                M[a, b] += 1; M[b, a] += 1
        if t < R - 1:
            vals = M[iu]; s = int(vals.max() - vals.min()); spreadW.append(s); spread = max(spread, s)
    vals = M[iu]
    res['lambda'] = (int(vals.min()), int(vals.max()))
    lo, hi = R // n, -(-R // n)
    res['lane_exact'] = bool(((lane >= lo) & (lane <= hi)).all()) if 0 not in [p for w in weeks for g in w for p in g] else bool((lane.max(1)-lane.min(1) <= 1).all())
    res['lane_range'] = (int(lane.min()), int(lane.max()), int((lane.max(1)-lane.min(1)).max()))
    res['pos_spread'] = int((pos.max(1) - pos.min(1)).max())
    res['prefix_spread'] = spread
    res['distinct_weeks'] = len({frozenset(frozenset(g) for g in w) for w in weeks})
    if any(vac_lane): res['vac_lane'] = vac_lane
    # greedy minimum clash-free blocks for this order
    blocks = []; seen = set(); cur = 0
    for w in weeks:
        pr = {frozenset(e) for g in w for e in itertools.combinations([p for p in g if p], 2)}
        if pr & seen: blocks.append(cur); seen = set(); cur = 0
        seen |= pr; cur += 1
    blocks.append(cur); res['greedy_blocks'] = blocks
    if pattern and pattern[0] is not None:
        bl = [len(list(g)) for _, g in itertools.groupby(pattern)]
        rep = 0; start = 0
        for b in bl:
            C = collections.Counter(frozenset(e) for w in weeks[start:start+b] for g in w for e in itertools.combinations([p for p in g if p], 2))
            rep += sum(c-1 for c in C.values()); start += b
        res['blocks'] = bl; res['block_repeats'] = rep
    return res
if __name__ == '__main__':
    for f in sys.argv[1:]:
        for s in parse(f):
            r = analyse(s['weeks'], s['pattern'])
            print(f.split('/')[-1], '|', s['title']); print('   ', r)
