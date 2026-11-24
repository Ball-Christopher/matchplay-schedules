"""Write the RTD-based files (see rtd.py)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import finish
from rtd import v36_049, v32_409
if __name__ == '__main__':
    secs = float(sys.argv[1]) if len(sys.argv) > 1 else 30
    finish(36, v36_049(), 'v36_0-4-9.json', 'resolvable TD(4,9) over GF(9) (9 four-way weeks: blocks {(i, a + b*e_i)}, b fixes the week) with each group of 9 filled by KTS(9) = AG(2,3) (4 three-way weeks)', seconds=secs)
    finish(32, v32_409(), 'v32_4-0-9.json', 'resolvable TD(4,8) over GF(8) (8 four-way weeks) with each group of 8 split into two K4s (1 four-way week) and the K_{4,4} between them 1-factored (4 two-way weeks, wrapped two matches per lane pair)', seconds=secs)
