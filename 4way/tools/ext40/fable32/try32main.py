import sys, json, random
sys.path.insert(0, '..')
from finish import *
for path in sys.argv[1:]:
    d = json.load(open(path)); W = [[[p + 1 for p in g] for g in wk] for wk in d["weeks"]]
    for seed in (1, 2):
        W1, _ = order_blocks(W, 32, list(range(1, 33)), [31], random.Random(seed), 60000)
        st = stats(W1, 32, 4); print(path, seed, max(st["prefix_spread"][:-1]), sum(x * x for x in st["prefix_spread"]), flush=True)
