"""LNS repair for a full lambda=3 schedule: free a few weeks, re-solve them with z3
so pair totals stay exact and every prefix sits in the annealer's windows."""
import json, sys, random, time
from itertools import combinations
from z3 import Bool, Solver, And, Or, PbEq, PbLe, PbGe, sat, is_true
import anneal_prefix as A
v = int(sys.argv[1]); src = sys.argv[2]; secs = float(sys.argv[3]); lam = 3
W = json.load(open(src))["weeks"]; r = len(W); n = v // 4
lo, hi = A.windows(v, lam, 2)
def viol(W):
    idx = {p: i for i, p in enumerate(combinations(range(1, v + 1), 2))}; c = [0] * len(idx); bad = 0; badW = []
    for t, wk in enumerate(W):
        for G in wk:
            for a, b in combinations(sorted(G), 2): c[idx[(a, b)]] += 1
        k = sum(1 for x in c if x < lo[t + 1] or x > hi[t + 1]); bad += k
        if k: badW.append(t)
    return bad, badW
rng = random.Random(int(sys.argv[4]) if len(sys.argv) > 4 else 0)
cur, badW = viol(W); t0 = time.time(); print("start", cur, badW, flush=True)
while cur and time.time() - t0 < secs:
    free = set(rng.sample(badW, min(2, len(badW))))
    while len(free) < int(sys.argv[5] if len(sys.argv) > 5 else 4):
        free.add(rng.randrange(r))
    free = sorted(free)
    S = Solver(); S.set("timeout", 60000)
    x = {(w, p, g): Bool(f"x{w}_{p}_{g}") for w in free for p in range(1, v + 1) for g in range(n)}
    for w in free:
        for p in range(1, v + 1): S.add(PbEq([(x[(w, p, g)], 1) for g in range(n)], 1))
        for g in range(n): S.add(PbEq([(x[(w, p, g)], 1) for p in range(1, v + 1)], 4))
        S.add(x[(w, 1, 0)])
    fixed_meet = {}
    for a, b in combinations(range(1, v + 1), 2):
        ms = {}
        for w in free:
            ms[w] = Or([And(x[(w, a, g)], x[(w, b, g)]) for g in range(n)])
        cum = 0; lits = []
        for t in range(r):
            if t in ms: lits.append((ms[t], 1))
            else: cum += any(a in G and b in G for G in W[t])
            L_, H_ = lo[t + 1] - cum, hi[t + 1] - cum
            if t + 1 == r: L_ = H_ = lam - cum
            if lits:
                if H_ < len(lits): S.add(PbLe(lits, H_))
                if L_ > 0: S.add(PbGe(lits, L_))
            else:
                if L_ > 0 or H_ < 0: S.add(False)
    if S.check() == sat:
        M = S.model()
        new = [wk[:] for wk in W]
        for w in free:
            new[w] = [[p for p in range(1, v + 1) if is_true(M.evaluate(x[(w, p, g)]))] for g in range(n)]
        c2, b2 = viol(new)
        if c2 <= cur:
            W, cur, badW = new, c2, b2
            print("  ", round(time.time() - t0), "free", free, "->", cur, badW, flush=True)
            json.dump({"weeks": W, "violations": cur}, open(f"lns_v{v}.json", "w"))
print("final", cur)
