"""v24 0-1-7 lanes: z3 (lanes_sat.solve_lanes) with at most K bowlers off, K decreasing,
on the library design or on fresh 4-RGDD(3^8) designs from the cyclic template.
usage: python3 lanes017k.py <file|gen:seed> K_start [timeout]"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lanes_sat import solve_lanes
from regroup import load_weeks
HERE = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1]; K = int(sys.argv[2]); to = int(sys.argv[3]) if len(sys.argv) > 3 else 300
if src == 'file': v, W = load_weeks('v24_0-1-7.json')
else:
    import convsearch; v = 24; W = convsearch.gen('rgdd3_8', int(src[4:]))
W = sorted(W, key=lambda wk: -len(wk[0]))
while K >= 2:
    t = time.time(); r, sol = solve_lanes(v, W, 8, K, timeout=to)
    print(src, 'K', K, r, round(time.time() - t, 1), flush=True)
    if r != 'sat': break
    json.dump({'weeks': W, 'slots': sol[0], 'caps': sol[1]}, open(os.path.join(HERE, 'out', f'lanes017k_{src.replace(":", "")}_{K}.json'), 'w'))
    K -= 1
