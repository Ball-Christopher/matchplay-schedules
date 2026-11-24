"""v20 (4,0,5): z3 direct model (sat.py 20 4,4,4,4,4,2,2,2,2) -> out/sat20_405.txt.
(1,0,6) is impossible: its 4-way weeks would be 6 weeks of 5 fours with no couple
repeated, but 20 bowlers in fours manage at most 5 such weeks (social golfer 5-4-5 is
the maximum; equivalently there is no 4-RGDD of type 2^10)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import build, best_lanes
HERE = os.path.dirname(os.path.abspath(__file__))
W = json.load(open(os.path.join(HERE, 'out', 'sat20_405.txt')))
from lanes_sat import solve_lanes
r, (sl, cp) = solve_lanes(20, W, 5, 0)
build(20, W, lanes=(sl, cp), method='direct z3 model (sat.py), 5 weeks 4-way + 4 weeks 2-way; 2-way weeks wrapped two matches per lane pair; lanes exact by z3 (lanes_sat.py), positions by de Werra colouring', fname='v20_4-0-5.json')
