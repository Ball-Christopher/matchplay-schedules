import sys; sys.path.insert(0, '.')
from finish import *
M32 = ("Z_8 x 4 classes (point 8*class+i), automorphism i->i+1 also moving every group up one lane pair. "
       "3 base weeks developed mod 8 (24 weeks), tied by the class map phi=(0)(1 2 3); 4 Z_8-invariant transversal weeks "
       "(one phi-orbit of 3 plus 1 phi-fixed) and 3 'half' weeks whose groups {(x,t),(x,t+4),(y,b+t),(y,b+t+4)} have "
       "orbit length 4 and cover the antipodal pairs {i,i+4} once each (developed base weeks would cover them twice, so "
       "some such week is forced for lambda=3). Pair balance by annealing on pair-orbit counts (ext40/zsym.c, PHI=1, seconds). "
       "Lanes NOT exact: the half weeks cannot rotate with the lanes, and every lane search (residue annealing, z3, general "
       "annealing) stopped at 16 bowler-lane cells at 5 instead of 4 (13 bowlers off by one on one lane pair). "
       "Week order annealed for prefix spread; positions by equitable bipartite edge-colouring.")
finish_main(32, "p32_best.txt", M32, steps=80000)
