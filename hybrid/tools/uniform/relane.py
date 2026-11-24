"""Re-anneal the lanes of existing uniform files with lanes.c (longer runs, several weights);
rewrite a file only when fewer bowlers are off.  usage: python3 relane.py seconds procs file..."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import clanes, build, HYB
from regroup import load_weeks
import verify
secs, procs = float(sys.argv[1]), int(sys.argv[2])
for fn in sys.argv[3:]:
    path = os.path.join(HYB, 'files', fn); d = json.load(open(path))
    v, W = load_weeks(fn); n = d['lane_pairs']; W = sorted(W, key=lambda wk: -len(wk[0]))
    old = verify.check(path)['lane_off_bowlers']; best = None
    for Wt in (3, 10, 30):
        sl, cp, off = clanes(v, W, n, seconds=secs, procs=procs, W=Wt, seed=7 * Wt)
        print(fn, 'W', Wt, 'off', off, 'was', old, flush=True)
        if best is None or off < best[0]: best = (off, sl, cp)
        if off == 0: break
    if best[0] < old:
        meth = d['method']
        if 're-annealed' not in meth: meth += '; lanes re-annealed (relane.py)'
        extra = {k: x for k, x in d.items() if k not in ('players', 'lane_pairs', 'weeks', 'method')}
        build(v, W, meth, fn, n=n, lanes=(best[1], best[2]), extra=extra)
