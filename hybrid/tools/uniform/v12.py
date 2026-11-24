"""v12 uniform hybrids via z3 (sat.py).  Facts used: two 4-way weeks on 12 bowlers always
share a couple (pigeonhole: the 4 bowlers of a group in week 2 come from only 3 groups of
week 1), so a4 <= 1; NKTS(12) does not exist (z3 confirms), so a3 <= 4 when a4 = 0."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sat import solve
from common import build, best_lanes
for ks, a in [((4, 3, 3, 3, 3), '0-4-1'), ((3, 3, 3, 3, 2, 2, 2), '3-4-0'), ((3, 3, 2, 2, 2, 2, 2, 2, 2), '7-2-0')]:
    W = solve(12, list(ks), 120)
    Wb, sl, cp, off = best_lanes(12, [W], tries=6, iters=300000, restarts=4)
    build(12, Wb, lanes=(sl, cp), method=f'direct z3 model (sat.py), week sizes {ks}; lanes by annealing, positions by de Werra colouring', fname=f'v12_{a}.json')
