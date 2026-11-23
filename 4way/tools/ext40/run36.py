import sys; sys.path.insert(0, '.')
from finish import *
M36 = ("Z_9 x 4 classes (point 9*class+i), automorphism i->i+1 also moving every group up one lane pair. "
       "3 base weeks developed mod 9 (27 weeks), tied by the class map phi=(0)(1 2 3) (base week w+1 = phi(base week w)); "
       "8 Z_9-invariant transversal weeks (two phi-orbits of 3 plus 2 phi-fixed). Pair balance by simulated annealing on "
       "pair-orbit counts (ext40/zsym.c, PHI=2, about 40 s); lane permutations of the base weeks and offsets of the invariant "
       "weeks by annealing on lane residues, exact. Week order annealed for prefix spread; positions by equitable "
       "bipartite edge-colouring (positions.assign).")
finish_main(36, "p36.txt", M36, steps=int(sys.argv[1]) if len(sys.argv)>1 else 20000)
