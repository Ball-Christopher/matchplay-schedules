"""v24 5-0-6: URD({2,4};24) with r2 = 5 from the labeled {2,4}-LRGDD_2 of type 2^6
(r2 = 5, r4 = 5) in the online resource of E. Schuster and G. Ge, Des. Codes Cryptogr. 57
(2010), Example A.15 (transcribed in out/schuster_ge_A15_labeled.json), expanded by 2
(each point x -> 2 points, block (x1..xk; labels) -> 2 blocks) and the 6 groups of 4
added as a 4-way week."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import finish
HERE = os.path.dirname(os.path.abspath(__file__))
def design():
    rows = json.load(open(os.path.join(HERE, 'out', 'schuster_ge_A15_labeled.json')))
    P = lambda a, j: 2 * (a - 1) + (j % 2) + 1
    W = [[[P(pts[0], j)] + [P(pts[i], j + phi[i - 1]) for i in range(1, len(pts))] for pts, phi in r for j in range(2)] for r in rows]
    W.append([[P(a, 0), P(a, 1), P(a + 1, 0), P(a + 1, 1)] for a in range(1, 13, 2)])
    return W
if __name__ == '__main__':
    finish(24, design(), 'v24_5-0-6.json', 'E. Schuster and G. Ge, Des. Codes Cryptogr. 57 (2010), online resource Example A.15: labeled {2,4}-LRGDD_2 of type 2^6 expanded by 2, plus the groups as a 4-way week; 2-way weeks wrapped two matches per lane pair', seconds=float(sys.argv[1]) if len(sys.argv) > 1 else 30, procs=1)
