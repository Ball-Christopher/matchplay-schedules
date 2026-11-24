"""Improve the lanes of an existing uniform file: z3 (lanes_sat.solve_lanes) with at most K
bowlers off, K = current - 1 downwards; each success rewrites the file (same weeks, same
method text plus a note).
usage: python3 improve_lanes.py v24_0-4-5.json [timeout_per_K]"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lanes_sat import solve_lanes
from regroup import load_weeks
from common import build, HYB, lane_off
import verify

def main(fn, to):
    path = os.path.join(HYB, 'files', fn)
    d = json.load(open(path)); v, W = load_weeks(fn); n = d['lane_pairs']
    W = sorted(W, key=lambda wk: -len(wk[0]))
    off = verify.check(path)['lane_off_bowlers']
    meth = d['method']
    if 'z3 lane' not in meth:
        meth = meth.replace('lane pairs by simulated annealing (lanes.c)', 'lane pairs by simulated annealing (lanes.c) then z3 lane search (improve_lanes.py)')
        meth = meth.replace('lane pairs by annealing', 'lane pairs by annealing then z3 lane search (improve_lanes.py)')
    K = off - 1
    while K >= 0:
        t = time.time(); r, sol = solve_lanes(v, W, n, K, timeout=to)
        print(fn, 'K', K, r, round(time.time() - t, 1), flush=True)
        if r != 'sat': break
        extra = {k: x for k, x in d.items() if k not in ('players', 'lane_pairs', 'weeks', 'method')}
        build(v, W, meth, fn, n=n, lanes=sol, extra=extra)
        K = verify.check(path)['lane_off_bowlers'] - 1

if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 300)
