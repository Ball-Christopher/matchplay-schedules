"""v24 0-1-7: anneal lanes (lanes.c) on many fresh 4-RGDD(3^8) designs from the cyclic
template and keep the best (out/lanes017multi_best.json).
usage: python3 lanes017multi.py n_designs seconds_each seed0 [W]"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import clanes, lane_off
import convsearch
HERE = os.path.dirname(os.path.abspath(__file__))
nd, secs, s0 = int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]); Wt = int(sys.argv[4]) if len(sys.argv) > 4 else 10
best = None
for i in range(nd):
    W = convsearch.gen('rgdd3_8', s0 + i)
    if W is None: continue
    W = sorted(W, key=lambda wk: -len(wk[0]))
    sl, cp, off = clanes(24, W, 8, seconds=secs, procs=1, W=Wt, seed=s0 + i)
    print(s0 + i, off, flush=True)
    if best is None or off < best[0]:
        best = (off, W, sl, cp)
        json.dump({'off': off, 'weeks': W, 'slots': sl, 'caps': cp}, open(os.path.join(HERE, 'out', f'lanes017multi_{s0}.json'), 'w'))
print('best', best[0])
