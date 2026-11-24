"""Cyclic templates with the rows as an invariant week (v = m x rows, no fixed points):
the rows {(0,i),..,(m-1,i)} form one m-way week, covering every pure difference; base
classes developed mod m cover the mixed differences.  Also v20 (4,0,5) with 4 fixed
2-way weeks made of mixed-difference orbits."""
import os, sys, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cyclic import search_c, to_one_based
def rows_week(m, rows): return [[i * m + x for x in range(m)] for i in range(rows)]
def mixed_match(m, i, j, d): return [[i * m + x, j * m + (x + d) % m] for x in range(m)]
CASES = {
 'v24_045': (4, 6, [3, 4], lambda: [rows_week(4, 6)]),
 'v24_073': (3, 8, [3, 3, 4], lambda: [rows_week(3, 8)]),
 'v36_049': (4, 9, [3, 4, 4], lambda: [rows_week(4, 9)]),
 'v20_405': (5, 4, [4], lambda: [mixed_match(5, 0, 1, 0) + mixed_match(5, 2, 3, 0), mixed_match(5, 0, 1, 1) + mixed_match(5, 2, 3, 1),
                                 mixed_match(5, 0, 2, 0) + mixed_match(5, 1, 3, 0), mixed_match(5, 0, 3, 0) + mixed_match(5, 1, 2, 0)]),
}
if __name__ == '__main__':
    name = sys.argv[1]; m, rows, ks, fx = CASES[name]
    t = time.time(); W = search_c(m, rows, 0, ks, fx(), seed=int(os.environ.get('SEED', 1)), node_limit=int(os.environ.get('NL', 2000000)), time_limit=float(os.environ.get('TL', 60)))
    print(name, 'found' if W else 'NOT found', round(time.time() - t, 1), flush=True)
    if W: print(W)
