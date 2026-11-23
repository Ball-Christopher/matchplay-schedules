import sys, itertools, random, json
from gen import *
S = Sys(7, 4, 4)
def phi32(mu):
    return [S.pt((p // 7 + 1) % 4, mu * (p % 7)) if p < 28 else 28 + (p - 28 + 1) % 4 for p in range(32)]
if __name__ == "__main__":
    out = []
    for mu in (1, 6):
        phi = phi32(mu); tp = S.tperm(phi)
        trs = list(itertools.product(range(7), repeat=3))
        tt = {x: S.wtypes(S.transversal((0,) + x)) for x in trs}
        # mixed class-pair types only matter; phi-invariance of the count vector
        for T in itertools.combinations(trs, 3):
            invc = {}
            for x in T:
                for t in tt[x]: invc[t] = invc.get(t, 0) + 1
            if any(invc.get(tp[t], 0) != c for t, c in invc.items()): continue
            inv = [S.transversal((0,) + x) for x in T]
            for ks in itertools.permutations(range(4), 3):
                r = S.spec(phi, 4, True, inv, ks)
                if r and tie_feasible(S, phi, 4, *r): out.append((mu, T, ks))
        print(mu, len(out), flush=True)
    json.dump(out, open("cands32.json", "w"))
    for x in out[:20]: print(x)
