"""Write files from labeled-design searches (labeled_sat.py / labeled2.py outputs in out/)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import finish
HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = {
 'v32_1-0-10': ('labeled_2^16_1.json', 32, '4-RGDD of type 2^16 from a labeled resolvable (16,4,2) design with Z_2 labels (found by z3, labeled_sat.py) expanded by 2 (Shen / Schuster 2009 Thm 2.2); the 16 groups of 2 are the 2-way week (wrapped two matches per lane pair)'),
 'v36_0-1-11': ('labeled_3^12_1.json', 36, '4-RGDD of type 3^12 from a labeled resolvable (12,4,3) design with Z_3 labels (found by z3, labeled_sat.py) expanded by 3 (Shen / Schuster 2009 Thm 2.2); the 12 groups of 3 are the 3-way week'),
}
if __name__ == '__main__':
    secs = float(sys.argv[1]); names = sys.argv[2:]
    for name in names:
        src, v, meth = SPEC[name]
        W = json.load(open(os.path.join(HERE, 'out', src)))['weeks']
        finish(v, W, name + '.json', meth, seconds=secs, procs=2)
