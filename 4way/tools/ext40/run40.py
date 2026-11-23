import sys; sys.path.insert(0, '.')
from finish import *
M40 = ("Resolvable 2-(40,4,1) on (Z_13 x 3 classes) u {inf}, the analogue of v28: one base week whose 60 pairs cover every pair orbit "
       "exactly once, developed mod 13 (13 weeks); the base week is also fixed by (a,i)->(a+1,3i), which makes the exact-cover DFS "
       "instant (ext40/dfs13.c, PSI=3). Z_13 does not act on the 10 lane pairs, so lanes were searched directly: general annealing "
       "(lanesa.c) over 240 designs reached 2 excess cells at best, z3 PB timed out (unknown). Lanes NOT exact. The Z_10 x 4 lane-rotating "
       "route (1 base week + 2 transversal + 1 half week) found no design: annealing stalled at cost 8, and exhaustive DFS under every "
       "order-4 symmetry tried has no solution. Week order: lambda=1, any order has prefix spread 1; positions by positions.assign.")
W = finish_main(40, "w40_main.json", M40, steps=2000)
