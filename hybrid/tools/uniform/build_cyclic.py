"""Build hybrid/files from cyclic base-class search outputs (out/cyc_<name>.txt)."""
import ast, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import build
from cyclic import to_one_based
HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = {  # name: (v, file, method)
 'nkts18b': (18, 'v18_1-8-0.json', 'nearly Kirkman triple system NKTS(18): points Z_4 x 4 rows + 2 fixed, pair class {(x,i),(x+2,i)} + {inf0,inf1}, two base triple classes developed mod 4 (cyclic.py randomised backtracking)'),
 'nkts24': (24, 'v24_1-11-0.json', 'nearly Kirkman triple system NKTS(24): points Z_11 x 2 rows + 2 fixed, pair class {(x,0),(x,1)} + {inf0,inf1}, one base triple class developed mod 11 (cyclic.py)'),
 'nkts30b': (30, 'v30_1-14-0.json', 'nearly Kirkman triple system NKTS(30): points Z_7 x 4 rows + 2 fixed, pair class {(x,0),(x,1)},{(x,2),(x,3)} + {inf0,inf1}, two base triple classes developed mod 7 (cyclic.py)'),
 'nkts36': (36, 'v36_1-17-0.json', 'nearly Kirkman triple system NKTS(36): points Z_17 x 2 rows + 2 fixed, pair class {(x,0),(x,1)} + {inf0,inf1}, one base triple class developed mod 17 (cyclic.py)'),
 'rgdd3_8': (24, 'v24_0-1-7.json', '4-RGDD of type 3^8: points Z_7 x 3 rows + 3 fixed, groups {(x,0),(x,1),(x,2)} and {inf0,inf1,inf2} form the 3-way week, one base 4-way class developed mod 7 (cyclic.py)'),
 'rgdd3_12': (36, 'v36_0-1-11.json', '4-RGDD of type 3^12: points Z_11 x 3 rows + 3 fixed, groups {(x,0),(x,1),(x,2)} and {inf0,inf1,inf2} form the 3-way week, one base 4-way class developed mod 11 (cyclic.py)'),
 'v36_077': (36, 'v36_0-7-7.json', '1-rotational over Z_7: points Z_7 x 5 rows + inf, one base 3-way class and one base 4-way class, each developed mod 7 (cyclic.py)'),
 'rgdd2_10b': (20, 'v20_1-0-6.json', '4-RGDD of type 2^10: points Z_3 x 6 rows + 2 fixed, pair class {(x,2i),(x,2i+1)} + {inf0,inf1}, two base 4-way classes developed mod 3 (cyclic.py); 2-way week wrapped two matches per lane pair'),
 'rgdd2_16b': (32, 'v32_1-0-10.json', '4-RGDD of type 2^16: points Z_5 x 6 rows + 2 fixed, pair class {(x,2i),(x,2i+1)} + {inf0,inf1}, two base 4-way classes developed mod 5 (cyclic.py); 2-way week wrapped two matches per lane pair'),
}
def load_all(name):
    import glob
    out = []
    for fn in sorted(glob.glob(os.path.join(HERE, 'out', f'*_{name}*.txt'))):
        L = open(fn).read().split('\n')
        if L and L[0].startswith(name) and 'NOT' not in L[0] and len(L) > 1 and L[1].startswith('['):
            out.append(to_one_based(ast.literal_eval(L[1])))
    return out
def load(name):
    a = load_all(name); return a[0] if a else None
if __name__ == '__main__':
    for name in sys.argv[1:]:
        v, fn, meth = SPEC[name]; W = load(name)
        if W is None: print(name, 'no design'); continue
        W.sort(key=lambda wk: -len(wk[0]))
        build(v, W, meth + '; lane pairs by annealing, positions by de Werra colouring (tools/positions.py)', fn)
