"""Independent check: 24 bowlers, the seven 4-way weeks of hybrid/files/v24_0-1-7.json.
For every choice of 3 weeks to keep, list every way to fill the other 4 weeks with
clash-free 4-way weeks (any groupings) so the 7 weeks stay couple-disjoint.
Report the distinct 7-week packings other than the original, check Astra's
relabellings send the original to each one, and count the unmet triangles."""
import json, sys, itertools
import numpy as np
path, iso = sys.argv[1], sys.argv[2]
W = [[frozenset(g) for g in w if g and len(g) == 4] for w in json.load(open(path))["weeks"]]
W = [w for w in W if len(w) == 6]
assert len(W) == 7
P = list(range(1, 25)); E = {e: i for i, e in enumerate(itertools.combinations(P, 2))}
def pairs(g): return [E[p] for p in itertools.combinations(sorted(g), 2)]
def mask(week):
    m = 0
    for g in week:
        for e in pairs(g): m |= 1 << e
    return m
M = [mask(w) for w in W]
assert all(M[i] & M[j] == 0 for i in range(7) for j in range(i)), "original not couple-disjoint"
canon = lambda pack: frozenset(frozenset(w) for w in pack)
orig = canon(W)
found = {}
for keep in itertools.combinations(range(7), 3):
    used = M[keep[0]] | M[keep[1]] | M[keep[2]]
    quads = [frozenset(q) for q in itertools.combinations(P, 4) if not any(used >> e & 1 for e in pairs(q))]
    by_min = {}
    for q in quads: by_min.setdefault(min(q), []).append(q)
    weeks = []
    def rec(left, chosen):
        if not left: weeks.append(list(chosen)); return
        p = min(left)
        for q in by_min.get(p, []):
            if q <= left: chosen.append(q); rec(left - q, chosen); chosen.pop()
    rec(frozenset(P), [])
    ms = [mask(w) for w in weeks]
    A = np.array([[(m >> (64 * k)) & (2**64 - 1) for k in range(5)] for m in ms], dtype=np.uint64)
    adj = []
    for i in range(len(ms)):
        ok = ~np.any(A[i + 1:] & A[i], axis=1)
        adj.append(set((np.nonzero(ok)[0] + i + 1).tolist()))
    sols = 0
    for a in range(len(ms)):
        for b in adj[a]:
            ab = adj[a] & adj[b]
            for c in ab:
                for d in ab & adj[c]:
                    if c < d:
                        sols += 1
                        pack = canon([W[k] for k in keep] + [weeks[x] for x in (a, b, c, d)])
                        if pack != orig: found.setdefault(pack, []).append(keep)
    print(list(k + 1 for k in keep), len(weeks), sols, flush=True)
print("distinct alternatives:", len(found))
for pack, ks in found.items():
    print(" shares", len(pack & orig), "weeks with the original; found keeping", [[k + 1 for k in x] for x in ks])
# Astra's relabellings: decode their bitmask weeks only to compare as sets
cert = json.load(open(iso))
def from_bits(x): return frozenset(i + 1 for i in range(24) if x >> i & 1)
hit = set()
for c in cert:
    perm = c.get("player_image") or c.get("permutation") or c.get("perm") or c.get("map")
    alt = canon([frozenset(from_bits(g) for g in w) for w in c["alternative"]]) if isinstance(c["alternative"][0][0], int) else None
    mp = (lambda x: perm[x - 1] + (1 if min(perm) == 0 else 0)) if isinstance(perm, list) else (lambda x: perm[str(x)])
    img = canon([frozenset(frozenset(mp(x) for x in g) for g in w) for w in W])
    print(" certificate: image is one of my alternatives:", img in found, "| equals its stated alternative:", alt is None or img == alt)
    hit.add(img)
print("certificates cover all alternatives:", hit == set(found))
# unmet couples in the original
un = set(itertools.combinations(P, 2)) - {tuple(sorted(p)) for w in W for g in w for p in itertools.combinations(g, 2)}
import collections
deg = collections.Counter(x for e in un for x in e)
tri = [t for t in itertools.combinations(P, 3) if all(tuple(sorted(p)) in un for p in itertools.combinations(t, 2))]
print("unmet couples", len(un), "degrees", set(deg.values()), "triangles", len(tri), "disjoint", len(set().union(*map(set, tri))) == 3 * len(tri))
