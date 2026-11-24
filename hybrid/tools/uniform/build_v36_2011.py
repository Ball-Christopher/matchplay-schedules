"""Write v36_2-0-11 from v36_2011.py output."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import finish
HERE = os.path.dirname(os.path.abspath(__file__))
W = json.load(open(os.path.join(HERE, 'out', sys.argv[1])))
finish(36, W, 'v36_2-0-11.json', 'URD({2,4};36) with r2 = 2 invariant under Z_9 (points Z_9 x 4 rows): one base 4-way class developed mod 9, two 4-way weeks that are orbits of a transversal block, two 2-way weeks made of mixed-difference edge orbits (z3, v36_2011.py); 2-way weeks wrapped two matches per lane pair', seconds=float(sys.argv[2]), procs=2)
