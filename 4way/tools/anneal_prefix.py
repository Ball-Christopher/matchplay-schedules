"""Simulated annealing over full schedules (lambda=3 cases): exact pair balance
over the cycle plus every prefix inside the band [floor(lam*W/(v-1)), ceil(...)],
i.e. prefix spread <= 1 for every W."""
import json, math, random, sys, time
from itertools import combinations
def windows(v, lam, width):
    r = lam * (v - 1) // 3
    lo, hi = [], []
    for W in range(r + 1):
        a = lam * W / (v - 1)
        if width <= 1 or W in (0, 1, r - 1, r):
            lo.append(math.floor(a)); hi.append(math.ceil(a))
        else:
            c = round(a)
            lo.append(max(0, c - 1)); hi.append(max(0, c - 1) + 2)
    return lo, hi
def run(v, lam, seed, tlimit, init=None, width=1, Tmin=0.15):
    n = v // 4; r = lam * (v - 1) // 3
    lo, hi = windows(v, lam, width)
    rng = random.Random(seed)
    # grp[w][p] = group index of player p in week w
    if init:
        grp = [[0]*v for _ in range(r)]
        for w, wk in enumerate(init):
            for g, G in enumerate(wk):
                for p in G: grp[w][p-1] = g
    else:
        grp = []
        for w in range(r):
            pl = list(range(v)); rng.shuffle(pl)
            row = [0]*v
            for i, p in enumerate(pl): row[p] = i // 4
            grp.append(row)
    members = [[[p for p in range(v) if grp[w][p]==g] for g in range(n)] for w in range(r)]
    meet = [[[0]*r for _ in range(v)] for _ in range(v)]  # meet[a][b][w]
    for w in range(r):
        for G in members[w]:
            for a, b in combinations(G, 2):
                meet[a][b][w] = meet[b][a][w] = 1
    def pcost(a, b):
        m = meet[a][b]; c = 0; s = 0
        for W in range(1, r + 1):
            s += m[W-1]
            if s < lo[W]: c += lo[W] - s
            elif s > hi[W]: c += s - hi[W]
        return c + 4 * abs(s - lam)
    pc = {}
    total = 0
    for a, b in combinations(range(v), 2):
        pc[(a,b)] = pcost(a,b); total += pc[(a,b)]
    T = 1.0; t0 = time.time(); best = total; it = 0
    while total > 0 and time.time() - t0 < tlimit:
        it += 1
        w = rng.randrange(r)
        g1, g2 = rng.sample(range(n), 2)
        i1, i2 = rng.randrange(4), rng.randrange(4)
        A, B = members[w][g1], members[w][g2]
        a, b = A[i1], B[i2]
        oa = [x for x in A if x != a]; ob = [x for x in B if x != b]
        aff = [(a,x) for x in oa]+[(b,x) for x in ob]+[(a,x) for x in ob]+[(b,x) for x in oa]
        for x in oa: meet[a][x][w]=meet[x][a][w]=0; meet[b][x][w]=meet[x][b][w]=1
        for x in ob: meet[b][x][w]=meet[x][b][w]=0; meet[a][x][w]=meet[x][a][w]=1
        newc = {}
        d = 0
        for p, q in aff:
            k = (p,q) if p<q else (q,p)
            newc[k] = pcost(*k); d += newc[k] - pc[k]
        if d <= 0 or rng.random() < math.exp(-d / T):
            A[i1], B[i2] = b, a
            grp[w][a], grp[w][b] = g2, g1
            pc.update(newc); total += d
            if total < best: best = total
        else:
            for x in oa: meet[a][x][w]=meet[x][a][w]=1; meet[b][x][w]=meet[x][b][w]=0
            for x in ob: meet[b][x][w]=meet[x][b][w]=1; meet[a][x][w]=meet[x][a][w]=0
        T = max(Tmin, T * 0.999995)
        if it % 200000 == 0:
            print(f"  v={v} seed={seed} it={it} cost={total} best={best} T={T:.3f}", flush=True)
    weeks = [[sorted(p+1 for p in G) for G in members[w]] for w in range(r)]
    return total, weeks
if __name__ == "__main__":
    v = int(sys.argv[1]); tl = float(sys.argv[2]); seed = int(sys.argv[3]) if len(sys.argv)>3 else 1
    width = int(sys.argv[4]) if len(sys.argv)>4 else 1
    init = json.load(open(sys.argv[5]))["weeks"] if len(sys.argv)>5 else None
    cost, weeks = run(v, 3, seed, tl, init=init, width=width, Tmin=float(sys.argv[6]) if len(sys.argv)>6 else 0.3)
    print("final cost", cost)
    json.dump({"cost": cost, "weeks": weeks}, open(f"anneal_v{v}_s{seed}_w{width}.json","w"))
