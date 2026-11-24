"""Try alternative designs (labeled2.py, different z3 seeds) for a mix whose file has
lane-off bowlers; anneal each (lanes.c) and rewrite the file when one is better.
usage: python3 altlanes.py u g lam sizes fname n_designs lane_seconds [seed0]"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import labeled2
from common import clanes, build, HYB, check_design, lanes_needed
import verify
u, g, lam = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]); sizes = [int(x) for x in sys.argv[4].split(',')]
fn, nd, secs = sys.argv[5], int(sys.argv[6]), float(sys.argv[7]); s0 = int(sys.argv[8]) if len(sys.argv) > 8 else 100
path = os.path.join(HYB, 'files', fn)
for sd in range(s0, s0 + nd):
    r = labeled2.solve(u, g, lam, sizes, 300, sd)
    if isinstance(r, str): print(sd, r, flush=True); continue
    W = sorted(labeled2.expand(u, g, lam, r), key=lambda wk: -len(wk[0])); v = u * lam; check_design(v, W)
    n = json.load(open(path))['lane_pairs'] if os.path.exists(path) else lanes_needed(W)
    sl, cp, off = clanes(v, W, n, seconds=secs, procs=1, W=10, seed=sd)
    old = verify.check(path)['lane_off_bowlers'] if os.path.exists(path) else 10 ** 9
    print(sd, 'off', off, 'file', old, flush=True)
    if off < old:
        sz = sorted(sizes)
        meth = (f'labeled uniformly resolvable design on {u} points' + (f' with {u//g} groups of {g}' if g > 1 else '') +
                f', Z_{lam} labels, block sizes {sz} (z3 seed {sd}, labeled2.py), expanded by {lam} (Shen / Schuster 2009 Thm 2.2), '
                f'the expanded groups of {g*lam} as one more week; chosen among several such designs for its lanes (altlanes.py); '
                'lane pairs by simulated annealing (lanes.c), positions by de Werra colouring (tools/positions.py)')
        build(v, W, meth, fn, n=n, lanes=(sl, cp))
