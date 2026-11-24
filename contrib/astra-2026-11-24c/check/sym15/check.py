"""Independent cross-check: fixed-order backtracking over orbits (as specified).
usage: python3 check.py AMAX type"""
import sys, itertools, time

AMAX = int(sys.argv[1]); T = int(sys.argv[2])
words = [w for w in itertools.product(range(5), repeat=6)
         if sorted(w.count(l) for l in range(5)) == [1, 1, 1, 1, 2]]
assert len(words) == 1800
types = [(p, a, b) for p in (2, 3, 5) for a in range(6 // p + 1) for b in range(5 // p + 1) if a or b]
assert len(types) == 19
p, a, b = types[T]
def cyc(n, p, c):
    q = list(range(n))
    for j in range(c):
        for i in range(p):
            q[j*p+i] = j*p + (i+1) % p
    return q
sig, tau = cyc(6, p, a), cyc(5, p, b)
def act(w):
    o = [0]*6
    for i in range(6): o[sig[i]] = tau[w[i]]
    return tuple(o)
def ag(u, v): return sum(x == y for x, y in zip(u, v))
seen, orbs = set(), []
for w in words:
    if w in seen: continue
    o = [w]; x = act(w)
    while x != w: o.append(x); x = act(x)
    seen.update(o)
    if any(ag(u, v) > AMAX for u, v in itertools.combinations(o, 2)): continue
    orbs.append(o)
# fixed order: by lowest (week,lane) cell covered; then all cells below an orbit's
# lowest cell must already be full when we consider it (they can't be filled later)
def mincell(o): return min(i*5+w[i] for w in o for i in range(6))
orbs.sort(key=mincell)
n = len(orbs)
cells = [[0]*30 for _ in orbs]
for k, o in enumerate(orbs):
    for w in o:
        for i in range(6): cells[k][i*5+w[i]] += 1
ok = [[all(ag(u, v) <= AMAX for u in orbs[i] for v in orbs[j]) for j in range(n)] for i in range(n)]
mincell_ = [mincell(o) for o in orbs]
suffix = [0]*(n+1)
for k in range(n-1, -1, -1): suffix[k] = suffix[k+1] + len(orbs[k])
nodes = 0; sol = None
cnt = [0]*30; chosen = []
def rec(start, tot):
    global nodes, sol
    nodes += 1
    if tot == 15: sol = list(chosen); return True
    if tot + suffix[start] < 15: return False
    for k in range(start, n):
        if tot + suffix[k] < 15: return False
        m = mincell_[k]
        if any(cnt[c] < 3 for c in range(m)): return False
        if tot + len(orbs[k]) > 15: continue
        if any(cnt[c] + cells[k][c] > 3 for c in range(30)): continue
        if not all(ok[k][j] for j in chosen): continue
        for c in range(30): cnt[c] += cells[k][c]
        chosen.append(k)
        if rec(k+1, tot + len(orbs[k])): return True
        chosen.pop()
        for c in range(30): cnt[c] -= cells[k][c]
    return False
t0 = time.time()
rec(0, 0)
res = 'FOUND ' + ' '.join(''.join('ABCDE'[x] for x in w) for k in sol for w in orbs[k]) if sol else 'NONE'
print(f"py type {T:2d} {types[T]} AMAX={AMAX} usable={n} nodes={nodes} {res} {time.time()-t0:.1f}s", flush=True)
