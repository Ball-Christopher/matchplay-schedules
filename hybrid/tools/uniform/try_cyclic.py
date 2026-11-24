import sys, time, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cyclic import search, search_c
def groups_fixed(m, rows, f, half):
    F = rows*m
    if half == 'pairs':  # {(x,2i),(x,2i+1)}
        wk = [[2*i*m+x, (2*i+1)*m+x] for i in range(rows//2) for x in range(m)]
    elif half:  # {(x,i),(x+m/2,i)}
        wk = [[i*m+x, i*m+x+m//2] for i in range(rows) for x in range(m//2)]
    else:     # vertical {(x,0..rows-1)}
        wk = [[i*m+x for i in range(rows)] for x in range(m)]
    return [wk + [[F+j for j in range(f)]]]
cases = {
 'nkts18': (8,2,2,[3],True), 'nkts24': (11,2,2,[3],False), 'nkts30': (14,2,2,[3],True), 'nkts36': (17,2,2,[3],False),
 'rgdd2_10': (6,3,2,[4],True), 'rgdd2_16': (10,3,2,[4],True), 'rgdd3_8': (7,3,3,[4],False), 'rgdd3_12': (11,3,3,[4],False),
 'v36_077': (7,5,1,[3,4],None),
 'nkts18b': (4,4,2,[3,3],True), 'nkts30b': (7,4,2,[3,3],'pairs'), 'rgdd2_10b': (3,6,2,[4,4],'pairs'), 'rgdd2_16b': (5,6,2,[4,4],'pairs'),
}
for name in sys.argv[1:]:
    m, rows, f, ks, half = cases[name]
    fx = [] if half is None else groups_fixed(m, rows, f, half)
    t = time.time(); W = (search_c if os.environ.get("C") else search)(m, rows, f, ks, fx, seed=int(os.environ.get("SEED", 1)), node_limit=int(os.environ.get("NL", 300000)), time_limit=float(os.environ.get('TL', 240)))
    print(name, 'found' if W else 'NOT found', round(time.time()-t,1), flush=True)
    if W: print(W)
