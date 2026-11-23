"""Relabel a symmetric covering (sym_cover.py output) so that its 2 X weeks land on a pair
of parallel classes that is clash-free against v18_oil's last block C, with one of them
transversal to the owed-position classes (needs_trans=1).  The two X weeks form a cubic
bipartite graph on 6+6 trios (points = edges), so a relabelling exists iff the graphs are
isomorphic; all isomorphisms are enumerated and the one repeating fewest round-1 trios in
X+Y is kept.  usage: match.py sym.json out.json [needs_trans=1]"""
import sys, json, itertools
from common import *
src, out = sys.argv[1], sys.argv[2]; needs = int(sys.argv[3]) if len(sys.argv) > 3 else 1
tp = lambda t: list(itertools.combinations(t, 2))
T = [t for t in itertools.combinations(range(1, V + 1), 3) if not any(p in CP for p in tp(t))]
def classes(T):
    res = []
    def rec(used, cur):
        if len(cur) == 6: res.append(tuple(cur)); return
        x = min(p for p in range(1, V + 1) if p not in used)
        for t in T:
            if t[0] == x and not (set(t) & used): rec(used | set(t), cur + [t])
    rec(frozenset(), []); return res
PC = classes(T)
ps = [set(e for t in c for e in tp(t)) for c in PC]
tr = [all(len({SHORT[p] for p in t}) == 3 for t in c) for c in PC]
cands = []
for i, j in itertools.combinations(range(len(PC)), 2):
    if ps[i] & ps[j]: continue
    if tr[i]: cands.append((PC[i], PC[j]))
    if tr[j]: cands.append((PC[j], PC[i]))
    if not needs and not tr[i] and not tr[j]: cands.append((PC[i], PC[j])); cands.append((PC[j], PC[i]))
d = json.load(open(src)); W = [[tuple(t) for t in wk] for wk in d["weeks"]]
X1, X2 = W[0], W[1]
def isos(Ca, Cb):
    """all bijections sigma: points(0-based) -> 1..18 taking X1 -> Ca and X2 -> Cb"""
    res = []
    cb_of = {p: j for j, t in enumerate(Cb) for p in t}
    x2_of = {p: j for j, t in enumerate(X2) for p in t}
    for perm in itertools.permutations(range(6)):          # X1[i] -> Ca[perm[i]]
        # X2[j] must go to a Cb trio; determine via points
        m2 = {}; ok = True; sig = {}
        # each point p in X1[i] lies in X2[x2_of[p]]; its image q in Ca[perm[i]] lies in Cb[cb_of[q]]
        # need consistent map X2 index -> Cb index; try to build by backtracking over point images within trios
        def rec(i):
            if i == 6: res.append(dict(sig)); return
            src_t, dst_t = X1[i], Ca[perm[i]]
            for img in itertools.permutations(dst_t):
                added = []; good = True
                for p, q in zip(src_t, img):
                    a, b = x2_of[p], cb_of[q]
                    if m2.get(a, b) != b or (a not in m2 and b in m2.values()): good = False; break
                    if a not in m2: m2[a] = b; added.append(a)
                    sig[p] = q
                if good: rec(i + 1)
                for a in added: del m2[a]
        rec(0)
    return res
best = None; nmatch = 0
for Ca, Cb in cands:
    for sig in isos(Ca, Cb):
        nmatch += 1
        Wn = [[tuple(sorted(sig[p] for p in t)) for t in wk] for wk in W]
        rep = sum(t in R1T for wk in Wn for t in wk)
        if best is None or rep < best[0]: best = (rep, Wn)
print(src, "candidates", len(cands), "isomorphisms", nmatch, "best repeats", best[0] if best else None)
if best:
    Wn = best[1]; roles = d["roles"]
    idx = [0, 1] + [i for i in range(2, 9) if roles[i] == "E"] + [i for i in range(2, 9) if roles[i] == "L"]
    json.dump({"weeks": [[list(t) for t in Wn[i]] for i in idx], "repXY": best[0], "src": src}, open(out, "w")); print("FOUND", out)
