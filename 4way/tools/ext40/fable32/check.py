import sys, json, itertools
sys.path.insert(0, "../../../../tools"); sys.path.insert(0, "..")
from schedlib import stats
d = json.load(open(sys.argv[1])); W = [[[p + 1 for p in g] for g in wk] for wk in d["weeks"]]
v = 4 * len(W[0]); st = stats(W, v, 4)
print("weeks", len(W), "meet", st["meet"], "lane_off", st["lane_off"], "distinct weeks", len({frozenset(frozenset(g) for g in wk) for wk in W}))
