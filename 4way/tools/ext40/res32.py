"""Residue-level necessary condition for 32 (Z_8 x 4, 3 half weeks): the symmetric part's
per-class lane residue counts h[a][d] must be 4-periodic with values in {2,3,4}
(brute force over all h shows the only feasible patterns are 2,2,4^6 and 3^4,4^4).
Usage: python3 res32.py CANDFILE i0 i1"""
import sys, z3, json
sys.path.insert(0, '.')
from lanes_z3 import parse
txt = open(sys.argv[1]).read(); chunks = ["CAND" + c for c in txt.split("CAND")[1:]]
for idx in range(int(sys.argv[2]), int(sys.argv[3])):
    base, tr, hb = parse(chunks[idx]); m = 8
    S = z3.Solver(); S.set("timeout", 20000)
    X = [[[z3.Bool(f"x{w}_{b}_{L}") for L in range(m)] for b in range(m)] for w in range(3)]
    R = [[z3.Bool(f"r{f}_{L}") for L in range(m)] for f in range(len(tr))]
    one = lambda vs: S.add(z3.PbEq([(v, 1) for v in vs], 1))
    for w in range(3):
        for b in range(m): one(X[w][b])
        for L in range(m): one([X[w][b][L] for b in range(m)])
    for f in range(len(tr)): one(R[f])
    S.add(X[0][0][0])
    for a in range(4):
        hs = []
        for d in range(m):
            terms = []
            for w, bw in enumerate(base):
                for b in range(m):
                    for q in bw[4*b:4*b+4]:
                        if q // m == a: terms.append(X[w][b][(d + q % m) % m])
            for f, cf in enumerate(tr): terms.append(R[f][(d + cf[a]) % m])
            hs.append(z3.Sum([z3.If(t, 1, 0) for t in terms]))
        for d in range(m):
            S.add(hs[d] >= 2, hs[d] <= 4)
            if d < 4: S.add(hs[d] == hs[d + 4])
    print(idx, S.check(), flush=True)
