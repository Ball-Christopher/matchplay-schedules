import sys; sys.path.insert(0, '..')
from finish import *
M32 = ("Z_7 x 4 classes (point 7*class+i, i mod 7) plus 4 fixed bowlers: the map i->i+1 moves lane pairs 1-7 up one and fixes "
       "lane pair 8. A group of odd order avoids the Z_8 antipodal obstruction (an involution acting freely on bowlers must fix a lane pair). "
       "Same design as v32_oil: 4 base weeks developed mod 7 (28 weeks) = W, alpha(W), alpha^2(W) and an alpha-invariant W0, where "
       "alpha: (class c, i) -> (pi(c), 2i), pi = (0)(1 2 3); 3 invariant weeks T, alpha(T), alpha^2(T) = the four fixed bowlers on lane pair 8 "
       "plus a transversal group developed mod 7. W by exact backtracking on pair-orbit capacities (ext40/fable32/dfs.c, f21.py). "
       "In each base week one group of four class bowlers stays on lane pair 8 for its 7 weeks; the other 7 groups rotate. "
       "Lane counts depend on (lane - i) per class: DFS on residues (lanes.py), exact at once. "
       "Week order annealed freely for prefix spread (worst 2); positions by equitable bipartite edge-colouring (positions.assign).")
finish_main(32, sys.argv[1], M32, steps=int(sys.argv[2]) if len(sys.argv) > 2 else 80000)
