"""{2,4} hybrids from the library's resolvable (v,4,1) designs (4way/v16, v28, v40):
split s of the 4-way weeks into three 2-way weeks each (a K4 is three disjoint matchings
{ab|cd},{ac|bd},{ad|bc}).  Gives mix (3s, 0, r-s).  Also v12 cases via z3 (sat.py)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import build, best_lanes, HYB
LIB = os.path.join(os.path.dirname(HYB), '4way')
def rbibd(v):
    d = json.load(open(os.path.join(LIB, f'v{v}.json')))
    return [[wk[i:i + 4] for i in range(0, v, 4)] for wk in d['weeks']]
def split(weeks, s):
    out = weeks[s:]
    for wk in weeks[:s]:
        for pat in ((0, 1, 2, 3), (0, 2, 1, 3), (0, 3, 1, 2)):
            out.append([m for g in wk for m in ([g[pat[0]], g[pat[1]]], [g[pat[2]], g[pat[3]]])])
    return out
if __name__ == '__main__':
    for v, s in [(16, 1), (16, 2), (28, 1), (28, 2), (40, 1)]:
        W = rbibd(v); r = len(W)
        import itertools
        variants = [split([W[i] for i in c] + [W[i] for i in range(r) if i not in c], s) for c in itertools.combinations(range(r), s)][:12]
        Wb, sl, cp, off = best_lanes(v, variants, tries=3, iters=600000, restarts=3)
        build(v, Wb, lanes=(sl, cp), method= f'library resolvable ({v},4,1) design (4way/v{v}.json) with {s} of its {r} weeks split into three 2-way weeks each (K4 = 3 matchings); 2-way weeks wrapped two matches per lane pair; lanes by annealing, positions by de Werra colouring', fname=f'v{v}_{3*s}-0-{r-s}.json')
