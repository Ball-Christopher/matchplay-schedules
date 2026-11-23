"""Rotating-lane solve. Points Z_m x 4 (+ fixed points), lanes = m rotating (i -> i+1 moves lane l -> l+1)
plus `nfl` fixed lanes (0 or 1). Base week: one block per fixed lane stays there for all m translates,
the other m blocks get a bijection to Z_m. Invariant (transversal) week: translate j on lane r+j, the
fixed-point block on the fixed lane. Lane counts depend only on residue (lane - i) per class: DFS with cap hi."""
import random, itertools, sys, json

def solve(m, nfix, base, invoff, r_total, rng, node_limit=200000):
    """base: list of weeks (list of blocks of point ids); invoff: list of (0,a,b,c). Returns (weeks, info) or None."""
    ncl = 4; nl = m + (1 if nfix else 0); lo, hi = r_total // nl, -(-r_total // nl)
    isfix = lambda p: p >= m * ncl
    # choose fixed-lane blocks
    fixchoices = [[None]] * len(base)
    if nfix:
        fixchoices = [[b for b in range(len(wk)) if not any(isfix(p) for p in wk[b])] for wk in base]
    combos = list(itertools.product(*fixchoices)); rng.shuffle(combos)
    for fb in combos:
        if nfix:
            cc = [0] * ncl
            for wk, b in zip(base, fb):
                for p in wk[b]: cc[p // m] += 1
            if any(not lo <= x <= hi for x in cc): continue
        h = [[0] * m for _ in range(ncl)]
        offs = [rng.randrange(m) for _ in invoff]
        items = []  # (week, block, residue contributions for lane 0)
        for w, wk in enumerate(base):
            for b, g in enumerate(wk):
                if b == fb[w]: continue
                items.append((w, b, [(p // m, (-p) % m) for p in g if not isfix(p)]))
        for attempt in range(30):
            offs = [rng.randrange(m) for _ in invoff]
            h = [[0] * m for _ in range(ncl)]
            for o, r0 in zip(invoff, offs):
                for c in range(ncl): h[c][(r0 - o[c]) % m] += 1
            used = [[False] * m for _ in base]; asg = {}; nodes = [0]
            def dfs(i):
                if i == len(items): return True
                nodes[0] += 1
                if nodes[0] > node_limit: return False
                w, b, con = items[i]
                ls = [l for l in range(m) if not used[w][l]]; rng.shuffle(ls)
                for l in ls:
                    ok = True; done = []
                    for c, d in con:
                        x = (d + l) % m; h[c][x] += 1; done.append((c, x))
                        if h[c][x] > hi: ok = False; break
                    if ok:
                        used[w][l] = True; asg[(w, b)] = l
                        if dfs(i + 1): return True
                        used[w][l] = False
                    for c, x in done: h[c][x] -= 1
                return False
            if dfs(0) and all(lo <= x <= hi for row in h for x in row):
                sh = lambda p, k: p if isfix(p) else m * (p // m) + (p % m + k) % m
                W = []
                for w, wk in enumerate(base):
                    for k in range(m):
                        row = [None] * nl
                        for b, g in enumerate(wk):
                            L = m if b == fb[w] else (asg[(w, b)] + k) % m
                            row[L] = [sh(p, k) for p in g]
                        W.append(row)
                for o, r0 in zip(invoff, offs):
                    row = [None] * nl
                    for j in range(m): row[(r0 + j) % m] = [m * c + (o[c] + j) % m for c in range(ncl)]
                    if nfix: row[m] = list(range(m * ncl, m * ncl + nfix))
                    W.append(row)
                return W
    return None
