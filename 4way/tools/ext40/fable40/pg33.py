"""Parallelisms of PG(3,3) invariant under the order-5 Singer subgroup (n -> n+8 on Z_40),
with 3 fixed spreads + 2 spread orbits of length 5.  Output (one design per line, JSON):
{"fixed": [[A,B],...3], "orbit": [[10 blocks],[10 blocks]]}, points as [class, residue]
(n = class + 8*residue mod 40 ... class = n%8, residue = (n-class)/8)."""
import sys, json, itertools
# GF(81) = GF(3)[x]/(x^4+x+2)
def mul_x(v):  # v = (c0..c3)
    c0, c1, c2, c3 = v
    # x^4 = -x-2 = 2x+1
    return ((c3 * 1) % 3, (c0 + 2 * c3) % 3, c1, c2)
pw = [(1, 0, 0, 0)]
for i in range(79): pw.append(mul_x(pw[-1]))
assert len(set(pw)) == 80 and mul_x(pw[-1]) == (1, 0, 0, 0), "not primitive"
lg = {v: i for i, v in enumerate(pw)}
add = lambda u, v: tuple((a + b) % 3 for a, b in zip(u, v))
neg = lambda u: tuple((-a) % 3 for a in u)
lines = set()
for i in range(40):
    for j in range(i + 1, 40):
        u, v = pw[i], pw[j]
        lines.add(tuple(sorted({i, j, lg[add(u, v)] % 40, lg[add(u, neg(v))] % 40})))
lines = sorted(lines); assert len(lines) == 130 and all(len(l) == 4 for l in lines)
lid = {l: k for k, l in enumerate(lines)}
sh = lambda l, g: tuple(sorted((x + 8 * g) % 40 for x in l))
orb = {}; orbs = []
for l in lines:
    if l not in orb:
        o = [sh(l, g) for g in range(5)]; assert len(set(o)) == 5
        for m in o: orb[m] = len(orbs)
        orbs.append(o)
assert len(orbs) == 26
# invariant spreads: pairs of orbits partitioning the points
inv = [(a, b) for a in range(26) for b in range(a + 1, 26)
       if len({x for l in orbs[a] + orbs[b] for x in l}) == 40]
# all spreads with 10 distinct orbits
by_pt = [[l for l in lines if min(l) == p] for p in range(40)]
spreads = []
def dfs(used, cur, ob):
    if len(cur) == 10: spreads.append((frozenset(ob), tuple(cur))); return
    p = next(q for q in range(40) if not used >> q & 1)
    for l in by_pt[p]:
        m = sum(1 << x for x in l)
        if used & m or orb[l] in ob: continue
        dfs(used | m, cur + [l], ob | {orb[l]})
dfs(0, [], set())
print(len(inv), "invariant spreads;", len(spreads), "spreads with 10 distinct line orbits", file=sys.stderr)
# canonical rep per Z5-orbit of spreads: group by orbit-set + translate class
seen = set(); reps = []
for ob, s in spreads:
    key = min(tuple(sorted(sh(l, g) for l in s)) for g in range(5))
    if key in seen: continue
    seen.add(key); reps.append((ob, s))
print(len(reps), "spread orbits", file=sys.stderr)
invset = {frozenset(p): p for p in inv}
pt = lambda n: [n % 8, (n - n % 8) // 8]
out = 0
from collections import defaultdict
byob = defaultdict(list)
for ob, s in reps: byob[ob].append(s)
obs = list(byob)
for i1 in range(len(obs)):
    for i2 in range(i1, len(obs)):
        o1, o2 = obs[i1], obs[i2]
        if o1 & o2: continue
        rest = sorted(set(range(26)) - o1 - o2)
        # perfect matchings of rest (6 orbits) into invariant spreads
        def match(r):
            if not r: yield []; return
            a = r[0]
            for b in r[1:]:
                if frozenset((a, b)) in invset:
                    for m in match([x for x in r if x not in (a, b)]): yield [(a, b)] + m
        for m in match(rest):
            for s1 in byob[o1]:
                for s2 in byob[o2]:
                    if i1 == i2 and s1 >= s2: continue
                    d = {"fixed": [[[pt(x) for x in orbs[a][0]], [pt(x) for x in orbs[b][0]]] for a, b in m],
                         "orbit": [[[pt(x) for x in l] for l in s1], [[pt(x) for x in l] for l in s2]]}
                    print(json.dumps(d)); out += 1
print(out, "parallelisms", file=sys.stderr)
