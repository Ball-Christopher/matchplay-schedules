"""Check the five resolvable 2-(12,4,3) designs (results/designs12.json):
validity, simplicity, number of resolutions, and the exact minimum number of
within-block repeats for 3 and 4 blocks (minimum over all splits of the weeks)."""
import json, itertools, collections, sys
from functools import lru_cache
H = '0123456789TE'
P = {e: i for i, e in enumerate(itertools.combinations(range(12), 2))}
def minrep(weeks, b):
    W = [{P[e] for q in w for e in itertools.combinations(q, 2)} for w in weeks]
    n = len(W); cost = {}
    for m in range(1, 1 << n):
        s = set(); c = 0
        for i in range(n):
            if m >> i & 1: s |= W[i]; c += 1
        cost[m] = 18 * c - len(s)   # pair-slots minus distinct pairs = repeats
    @lru_cache(None)
    def f(m, k):
        if k == 1: return cost[m]
        low = m & -m; rest = m ^ low; best = 10**9; s = rest
        while True:
            t = s | low
            if t != m: best = min(best, cost[t] + f(m ^ t, k - 1))
            if s == 0: break
            s = (s - 1) & rest
        return best
    return f((1 << n) - 1, b)
def resolutions(rem):
    if not rem: return 1
    b0 = rem[0]; tot = 0
    for b1, b2 in itertools.combinations(rem[1:], 2):
        if len(set(b0) | set(b1) | set(b2)) == 12:
            tot += resolutions([b for b in rem if b not in (b0, b1, b2)])
    return tot
D = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'results/designs12.json'))
for n, d in enumerate(D, 1):
    weeks = [[tuple(sorted(H.index(c) for c in b)) for b in w] for w in d]
    blocks = [b for w in weeks for b in w]
    C = collections.Counter(e for b in blocks for e in itertools.combinations(b, 2))
    ok = all(sorted(x for b in w for x in b) == list(range(12)) for w in weeks) and len(C) == 66 and set(C.values()) == {3}
    print(n, 'valid', ok, 'simple', len(set(blocks)) == 33, 'resolutions', resolutions(sorted(blocks)),
          'min 3 blocks', minrep(weeks, 3), 'min 4 blocks', minrep(weeks, 4))
