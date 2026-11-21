#!/usr/bin/env python3
"""Step 1: build the resolvable 2-(v,4,lambda) designs (pair balance).

v=16: affine plane AG(2,4).
v=12, 24: 1-rotational over Z_m u {inf} (m = v-1), lambda=3, base week found by
          simulated annealing on pair-orbit counts, developed mod m.
v=28: 1-rotational over (Z_9 x 3 classes) u {inf}, lambda=1, base week found the
      same way, developed by +1 on the Z_9 coordinate (9 weeks).
Writes designs_raw.json: {v: {"weeks": [...], "lambda": l, "method": str}}
Weeks here are lists of groups (sets); lane order is decided later by lanes.py.
"""
import json, math, random, sys
from itertools import combinations

def ag24():
    # GF(4) = {0,1,a,a+1} as 0..3; addition = XOR
    mul = [[0]*4 for _ in range(4)]
    exp = [1, 2, 3]  # a^0=1, a^1=2(a), a^2=3(a+1)
    log = {1: 0, 2: 1, 3: 2}
    for x in range(1, 4):
        for y in range(1, 4):
            mul[x][y] = exp[(log[x] + log[y]) % 3]
    pid = lambda x, y: 4 * x + y + 1
    weeks = []
    for m in range(4):  # y = m x + c
        weeks.append([[pid(x, mul[m][x] ^ c) for x in range(4)] for c in range(4)])
    weeks.append([[pid(c, y) for y in range(4)] for c in range(4)])  # x = c
    return weeks

def rotational(v, m, lam, seed=0, max_iter=2_000_000):
    """Points 0..v-2 finite: class*m + x (x in Z_m); v-1 = inf. Group = Z_m."""
    inf = v - 1
    k = (v - 1) // m
    def tr(p, t):
        return p if p == inf else (p // m) * m + (p % m + t) % m
    orbit = {}
    norb = 0
    for a, b in combinations(range(v), 2):
        if (a, b) in orbit:
            continue
        for t in range(m):
            x, y = sorted((tr(a, t), tr(b, t)))
            orbit[(x, y)] = norb
        norb += 1
    rng = random.Random(seed)
    n = v // 4
    pts = list(range(v))
    while True:
        rng.shuffle(pts)
        blocks = [pts[4*i:4*i+4] for i in range(n)]
        hits = [0] * norb
        for B in blocks:
            for a, b in combinations(sorted(B), 2):
                hits[orbit[(a, b)]] += 1
        cost = sum((h - lam) ** 2 for h in hits)
        T = 2.0
        for it in range(max_iter):
            if cost == 0:
                break
            i, j = rng.sample(range(n), 2)
            pi, pj = rng.randrange(4), rng.randrange(4)
            a, b = blocks[i][pi], blocks[j][pj]
            delta = {}
            for c in blocks[i]:
                if c != a:
                    o = orbit[tuple(sorted((a, c)))]; delta[o] = delta.get(o, 0) - 1
                    o = orbit[tuple(sorted((b, c)))]; delta[o] = delta.get(o, 0) + 1
            for c in blocks[j]:
                if c != b:
                    o = orbit[tuple(sorted((b, c)))]; delta[o] = delta.get(o, 0) - 1
                    o = orbit[tuple(sorted((a, c)))]; delta[o] = delta.get(o, 0) + 1
            dc = sum((hits[o] + d - lam) ** 2 - (hits[o] - lam) ** 2 for o, d in delta.items())
            if dc <= 0 or rng.random() < math.exp(-dc / T):
                for o, d in delta.items():
                    hits[o] += d
                blocks[i][pi], blocks[j][pj] = b, a
                cost += dc
            T = max(0.05, T * 0.99995)
        if cost == 0:
            break
    weeks = []
    for t in range(m):
        weeks.append([sorted(tr(p, t) + 1 for p in B) for B in blocks])
    base = [sorted(B) for B in blocks]
    return weeks, base

def check(v, weeks, lam):
    cnt = {}
    for w in weeks:
        assert sorted(p for g in w for p in g) == list(range(1, v + 1))
        for g in w:
            for a, b in combinations(sorted(g), 2):
                cnt[(a, b)] = cnt.get((a, b), 0) + 1
    assert len(cnt) == v * (v - 1) // 2 and set(cnt.values()) == {lam}, (v, set(cnt.values()))

if __name__ == "__main__":
    out = {}
    w = ag24(); check(16, w, 1)
    out[16] = {"weeks": w, "lambda": 1, "method": "Affine plane AG(2,4): 5 parallel classes of lines over GF(4)^2."}
    for v, m, lam, label in [(12, 11, 3, "Z_11 u {inf}"), (24, 23, 3, "Z_23 u {inf}"),
                             (28, 9, 1, "(Z_9 x {0,1,2}) u {inf}")]:
        weeks, base = rotational(v, m, lam, seed=v)
        check(v, weeks, lam)
        print(v, "base week (0-based, inf=%d):" % (v - 1), base, flush=True)
        out[v] = {"weeks": weeks, "lambda": lam, "base": base,
                  "method": f"1-rotational over {label}: base week found by simulated annealing on pair-orbit counts, developed mod {m}."}
    json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else "designs_raw.json", "w"))
