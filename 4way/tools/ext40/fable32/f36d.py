"""36 oil in 4 blocks: Z_9 x 4 with alpha: (c,i)->(pi c, mu i + s_c), pi=(0)(1 2 3), alpha^3 in Z_9.
Base weeks W, aW, a^2W. 8 transversal invariant weeks: 2 alpha-fixed X, Y and two alpha-orbits O1, O2.
mode 1: block 4 = {X, Y}; O1 and O2 spread over the base blocks (a^k T1 and a^(k+j) T2 join block k): 11+11+11+2.
mode 2: block 4 = {X, Y} + O2 (pairwise disjoint); O1 spread: 10+10+10+5.
mode 3: five blocks 9+9+9+4+4, invariant weeks split {X}+O1 | {Y}+O2.
Usage: f36d.py mode seed nsamples nodelimit mu s0 s3"""
import sys, random, subprocess, json, itertools
from gen import *
S = Sys(9, 4, 0)
def off(wk):
    g = next(g for g in wk if 0 in g); o = [0] * 4
    for p in g: o[p // 9] = p % 9
    return tuple(o)
if __name__ == "__main__":
    mode, seed, ns, lim, mu, s0, s3 = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7])
    PI = [0, 2, 3, 1]; sv = [s0, 0, 0, s3]
    alpha = [S.pt(PI[p // 9], mu * (p % 9) + sv[p // 9]) for p in range(36)]
    a3 = [alpha[alpha[alpha[p]]] for p in range(36)]; assert len({(a3[p] - p) % 9 for p in range(36)}) == 1
    ap = lambda wk: [[alpha[p] for p in g] for g in wk]
    rng = random.Random(seed); orbs = {}
    for x in itertools.product(range(9), repeat=3):
        t = (0,) + x; o = [t]; w = S.transversal(t)
        for _ in range(2):
            w = ap(w); o.append(off(w))
        if min(o) not in orbs: orbs[min(o)] = o
    tt = lambda t: set(S.wtypes(S.transversal(t)))
    fixed = [o[0] for o in orbs.values() if len(set(o)) == 1]; full = [o for o in orbs.values() if len(set(o)) == 3]
    fp = [(x, y) for x, y in itertools.combinations(fixed, 2) if not tt(x) & tt(y)]
    print("fixed", len(fixed), "pairs", len(fp), "full", len(full), flush=True)
    done = tries = 0; tag = f"{mode}_{mu}_{s0}_{seed}"
    while done < ns:
        tries += 1
        X, Y = rng.choice(fp); O1, O2 = rng.sample(full, 2); j = rng.randrange(3)
        if mode == 1:
            tr = [X, Y] + O1 + O2[j:] + O2[:j]; blk = [-1, -1, 0, 1, 2, 0, 1, 2]
        elif mode == 2:
            if len(set().union(*[tt(t) for t in [X, Y] + O2])) != 30: continue
            tr = [X, Y] + O1 + O2; blk = [-1, -1, 0, 1, 2, -1, -1, -1]
        else:   # mode 3: five blocks 9+9+9+4+4: {X}+O1 and {Y}+O2 each pairwise disjoint (X, Y need not be)
            X, Y = rng.sample(fixed, 2) if rng.random() < .8 else (rng.choice(fixed),) * 2
            if len(set().union(*[tt(t) for t in [X] + O1])) != 24 or len(set().union(*[tt(t) for t in [Y] + O2])) != 24: continue
            tr = [X] + O1 + [Y] + O2; blk = [-1] * 8
        r = S.spec(alpha, 3, 3, [S.transversal(t) for t in tr], blk, None)
        path = f"s36d_{tag}.txt"
        if not r or not dfs_spec(S, alpha, 3, r[0], r[1], path): continue
        done += 1
        S.spec(alpha, 3, 3, [S.transversal(t) for t in tr], blk, path + ".sa")
        o1 = subprocess.run(["./sa", path + ".sa", str(seed * 1000 + done), "3000000", "1.5", "0.08", "2", "3"], capture_output=True, text=True).stdout
        c = int(o1.split("best=")[-1]); print("SA", seed, done, tries, c, tr, flush=True)
        if "SOL" in o1:
            json.dump({"mu": mu, "pi": PI, "s": sv, "tr": tr, "blk": blk, "sol": [l for l in o1.splitlines() if l.startswith("SOL")][0].split("|")[1]}, open(f"sol36d_{tag}_{done}.json", "w")); print("FOUND-SA", flush=True); continue
        if c > int(sys.argv[8]): continue
        out = subprocess.run(["./dfs", path, lim, "1", str(seed * 100 + done)], capture_output=True, text=True).stdout
        sol = [l for l in out.splitlines() if l.startswith("SOL")]
        print(seed, done, tries, tr, out.splitlines()[-1], flush=True)
        if sol:
            json.dump({"mu": mu, "pi": PI, "s": sv, "tr": tr, "blk": blk, "sol": sol[0]}, open(f"sol36d_{tag}_{done}.json", "w")); print("FOUND", flush=True)
