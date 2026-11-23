import sys, json
sys.path.insert(0, '.')
from lanes_z3 import parse, expand
from oilcolor import clash_graph, colour
txt = open(sys.argv[1]).read(); ch = ["CAND" + c for c in txt.split("CAND")[1:]]
res = []
for i, c in enumerate(ch):
    base, tr, hb = parse(c); m = len(base[0]) // 4
    W = expand(m, base, tr, hb, [list(range(m))] * len(base), [0] * len(tr), [list(range(m))] * len(hb))
    adj = clash_graph(W)
    for k in range(4, 20):
        col, r = colour(adj, k, limit=200000)
        if r: res.append((k, i)); print(i, k, flush=True); break
        if r is None: print(i, k, "limit", flush=True); break
print(sorted(res)[:5])
