# exploration: does a clash-free 8-week invariant block F exist at all for Z_9 x 4 (no extra symmetry)?
import random, itertools, sys
from gen import *
S = Sys(9, 4, 0); rng = random.Random(int(sys.argv[1]))
def types(B): return [S.type[a][b] for a, b in itertools.combinations(B, 2)]
trs = [(0,) + x for x in itertools.product(range(9), repeat=3)]
ttr = {t: frozenset(types([S.pt(c, t[c]) for c in range(4)])) for t in trs}
def rand_triple():
    while True:
        cos = [(c, r) for c in range(4) for r in range(3)]; rng.shuffle(cos)
        Bs = [[S.pt(c, r + 3 * rng.randrange(3)) for c, r in cos[i:i+4]] for i in (0, 4, 8)]
        ts = [t for B in Bs for t in types(B)]
        if len(set(ts)) == 18: return Bs, frozenset(ts)
def maxtr(used, need):
    cand = [t for t in trs if not ttr[t] & used]
    best = [0]
    def rec(i, u, k):
        if k > best[0]: best[0] = k
        if best[0] >= need: return
        for j in range(i, len(cand)):
            if not ttr[cand[j]] & u: rec(j + 1, u | ttr[cand[j]], k + 1)
            if best[0] >= need: return
    rec(0, used, 0); return best[0]
res = {}
for it in range(int(sys.argv[2])):
    Bs, u = rand_triple()
    k = maxtr(u, 5)
    # two triples
    k2 = None
    for _ in range(200):
        B2, u2 = rand_triple()
        if not u & u2: k2 = maxtr(u | u2, 2); break
    res[(k, k2)] = res.get((k, k2), 0) + 1
print(res)
