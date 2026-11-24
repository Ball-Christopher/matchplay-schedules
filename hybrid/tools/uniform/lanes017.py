import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common, build_cyclic as b
W = b.load('rgdd3_8'); W.sort(key=lambda wk: -len(wk[0]))
best = None
for sd in range(12):
    sl, c = common.anneal_lanes(24, W, 8, seed=sd, iters=2000000, restarts=1, W=10)
    off = common.lane_off(24, W, 8, sl, c); print(sd, off, flush=True)
    if best is None or off < best[0]: best = (off, sl, c)
import json; json.dump({'off': best[0], 'slots': best[1], 'caps': best[2]}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'lanes017.json'), 'w'))
