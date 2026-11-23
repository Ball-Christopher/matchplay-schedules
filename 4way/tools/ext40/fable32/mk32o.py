import sys, json, random, itertools
from f21 import *
from lanes import solve
d = json.load(open(sys.argv[1])); rng = random.Random(1)
W = [list(map(int, d["sol"].split()[1:]))[i:i+4] for i in range(0, 32, 4)]
ap = lambda wk: [[alpha[p] for p in g] for g in wk]
base = [W, ap(W), ap(ap(W)), d["W0"]]
T = S.transversal(d["T"]); invw = [T, ap(T), ap(ap(T))]
def off(wk):
    g = next(g for g in wk if 0 in g); o = [0] * 4
    for p in g: o[p // 7] = p % 7
    return tuple(o)
offs = [off(w) for w in invw]
Wk = solve(7, 4, base, offs, 31, rng)
print("lanes", Wk is not None)
# reorder into blocks: base k (7 weeks) + inv k
out = []
for k in range(4):
    out += Wk[7 * k:7 * k + 7]
    if k < 3: out.append(Wk[28 + k])
json.dump({"weeks": out, "base": base, "tr": offs, "half": [], "blocks": [8, 8, 8, 7]}, open(sys.argv[2], "w"))
