"""32 oil: Z_7 x| Z_3 (alpha: (c,i)->(pi c, 2i), pi=(0)(1 2 3), inf_j likewise). Blocks: [W orbit + T], [aW + aT], [a^2W + a^2T], [W0 orbit],
W0 alpha-invariant. Sample (W0, T), anneal W.  Usage: f21.py seed nsamples iters"""
import sys, random, subprocess, json, itertools
from gen import *
S = Sys(7, 4, 4); PI = [0, 2, 3, 1]
alpha = [S.pt(PI[p // 7], 2 * (p % 7)) if p < 28 else 28 + PI[p - 28] for p in range(32)]
def cyc(p): return [p, alpha[p], alpha[alpha[p]]]
def sample_W0(rng):
    cycles = [cyc(1), cyc(3)] + [cyc(7 + i) for i in range(7)]
    inf = cyc(29)
    while True:
        rng.shuffle(cycles)
        B2 = [28] + cycles[0]
        if cycles[0][0] < 7: continue
        B1 = [0] + cycles[1]
        rest = cycles[2:]; rng.shuffle(rest)
        o1 = [inf[0]] + [rng.choice(c) for c in rest[:3]]
        o2 = [rest[3][0]] + [rng.choice(c) for c in rest[4:7]]
        wk = [B1, B2]
        for o in (o1, o2):
            b = o
            for _ in range(3): wk.append(b); b = [alpha[p] for p in b]
        ts = [S.type[a][b] for g in wk for a, b in itertools.combinations(g, 2)]
        if len(set(ts)) == 48: return wk
if __name__ == "__main__":
    seed, ns, iters = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    A = sys.argv[4] if len(sys.argv) > 4 else "2"
    rng = random.Random(seed); done = 0
    while done < ns:
        W0 = sample_W0(rng); T = (0, rng.randrange(7), rng.randrange(7), rng.randrange(7))
        inv = [S.transversal(T)]
        for _ in range(2): inv.append([[alpha[p] for p in g] for g in inv[-1]])
        path = f"s21_{seed}.txt"
        r = S.spec(alpha, 3, 3, inv, (0, 1, 2), None, extra=[W0])
        if not r or not dfs_spec(S, alpha, 3, r[0], r[1], path, order=list(range(28, 32)) + list(range(28))): continue
        done += 1
        out = subprocess.run(["./dfs", path, iters, "1"], capture_output=True, text=True).stdout
        sol = [l for l in out.splitlines() if l.startswith("SOL")]
        print(seed, done, T, out.splitlines()[-1], flush=True)
        if sol:
            json.dump({"W0": W0, "T": T, "sol": sol[0]}, open(f"sol21_{seed}_{done}.json", "w")); print("FOUND", flush=True)
