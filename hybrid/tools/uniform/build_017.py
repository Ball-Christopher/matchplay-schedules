"""Rewrite v24_0-1-7 from a lane result in out/ (lanes017k.py z3 or lanes017multi.py
annealing), if it has fewer bowlers off than the current file."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import build, HYB
import verify
src, how = sys.argv[1], sys.argv[2]
d = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', src)))
old = verify.check(os.path.join(HYB, 'files', 'v24_0-1-7.json'))['lane_off_bowlers']
meth = ('4-RGDD of type 3^8: points Z_7 x 3 rows + 3 fixed, groups {(x,0),(x,1),(x,2)} and {inf0,inf1,inf2} form the 3-way week, '
        'one base 4-way class developed mod 7 (cyclic.py, ' + how + '); lane pairs by ' + ('z3 with at most K bowlers off (lanes017k.py)' if 'lanes017k' in src else 'simulated annealing over many such designs (lanes017multi.py)') +
        ', positions by de Werra colouring (tools/positions.py). Exact lanes are impossible (a lane pair gets 3 + 4x visits, never 24), so at least 2 bowlers are off')
caps = d.get('caps', [1] * len(d['weeks']))
r = build(24, d['weeks'], meth, 'v24_0-1-7.tmp.json', n=8, lanes=(d['slots'], caps))
if r['lane_off_bowlers'] < old:
    os.replace(os.path.join(HYB, 'files', 'v24_0-1-7.tmp.json'), os.path.join(HYB, 'files', 'v24_0-1-7.json')); print('written', r['lane_off_bowlers'], 'was', old)
else:
    os.remove(os.path.join(HYB, 'files', 'v24_0-1-7.tmp.json')); print('kept old', old)
