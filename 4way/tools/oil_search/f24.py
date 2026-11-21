import random
from finish import *
from chrom import colour, load
f="../fable1224/g24_1131_1.txt";W0=load(f);b,col=colour(W0)
W=[[w[i:i+4] for i in range(0,24,4)] for w in W0]
print("distinct weeks",len({frozenset(frozenset(g) for g in w) for w in W}),"b",b)
blks=[[W[i] for i in range(23) if col[i]==c] for c in range(b)]
finish("v24_oil",24,blks,"Lane-exact Z2^2 x Z3 design (1 free week x12, 1 Z3-invariant x4, 3 <k>xZ3-invariant x2, 1 coset week) from the earlier search pool (g24_1131_1); weeks split into the fewest clash-free blocks by exact colouring of the weeks-share-a-couple graph (8 blocks; b=4 was searched for with Z3x8, Z5x4+4 fixed points and Z2^2xZ3 structures but not found, and not proven impossible); block/week order annealed for prefix spread; positions by de Werra (positions.assign).",random.Random(5),steps=6000)
