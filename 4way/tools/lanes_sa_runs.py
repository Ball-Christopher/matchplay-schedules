import json, sys, lanes as L
src, secs, seed, out = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
W = json.load(open(src)); W = W["weeks"] if isinstance(W, dict) else W
X, c = L.balance_lanes_anneal(W, secs, seed)
print(src, seed, "excess", c, flush=True)
json.dump({"weeks": X, "excess": c}, open(out, "w"))
