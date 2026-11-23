"""36 oil, untied attempt: fourth block F = one <3>-fixed week orbit (3 base blocks) + 5 transversal weeks, all 48 pair types distinct
(found greedily at random); the 3 base weeks free, annealed with the clash penalty (sa.c, tie=1). Usage: f36u.py seed iters"""
import random, itertools, sys, subprocess, json
from gen import *
S = Sys(9, 4, 0); seed = int(sys.argv[1]); rng = random.Random(seed)
def types(B): return [S.type[a][b] for a, b in itertools.combinations(B, 2)]
trs = [(0,) + x for x in itertools.product(range(9), repeat=3)]
ttr = {t: frozenset(types([S.pt(c, t[c]) for c in range(4)])) for t in trs}
def rand_triple():
    while True:
        cos = [(c, r) for c in range(4) for r in range(3)]; rng.shuffle(cos)
        Bs = [[S.pt(c, r + 3 * rng.randrange(3)) for c, r in cos[i:i+4]] for i in (0, 4, 8)]
        ts = [t for B in Bs for t in types(B)]
        if len(set(ts)) == 18: return Bs, frozenset(ts)
def five(used):
    cand = [t for t in trs if not ttr[t] & used]; rng.shuffle(cand)
    def rec(i, u, acc):
        if len(acc) == 5: return acc
        for j in range(i, len(cand)):
            if not ttr[cand[j]] & u:
                r = rec(j + 1, u | ttr[cand[j]], acc + [cand[j]])
                if r: return r
        return None
    return rec(0, used, [])
while True:
    Bs, u = rand_triple(); tr = five(u)
    if tr: break
path = f"s36u_{seed}.txt"
r = S.spec(list(range(36)), 3, 1, [S.transversal(t) for t in tr], [-1] * 5, path, extra=[Bs])
out = subprocess.run(["./sa", path, str(seed), sys.argv[2], "1.5", "0.06", "2", "2"], capture_output=True, text=True, env={"VERB": "1"}).stdout
print(seed, Bs, tr, [l for l in out.splitlines() if not l.startswith("SOL")], flush=True)
sol = [l for l in out.splitlines() if l.startswith("SOL")]
if sol: json.dump({"triple": Bs, "tr": tr, "sol": sol[0]}, open(f"sol36u_{seed}.json", "w")); print("FOUND")
