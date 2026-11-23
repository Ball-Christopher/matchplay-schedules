#!/usr/bin/env python3
"""Class-bit permutations (78 bits: 60 cross then 18 inner) for candidate block-cycling automorphisms sigma:
 super-points permuted by sa, Z2^2 elements by phi.  Variants: 0: (012)(345), phi=id; 1: (012)(345), phi=(1 2 3);
 2: (012), phi=id; 3: (012), phi=(1 2 3)."""
import sys
PAIRS=[(x,y) for x in range(6) for y in range(x+1,6)]
V=[([1,2,0,4,5,3],[0,1,2,3]),([1,2,0,4,5,3],[0,2,3,1]),([1,2,0,3,4,5],[0,1,2,3]),([1,2,0,3,4,5],[0,2,3,1])]
for v,(sa,phi) in enumerate(V):
    with open(f"{sys.argv[1]}.sig{v}","w") as f:
        for b in range(60):
            pi,d=divmod(b,4); a,bb=PAIRS[pi]; a2,b2=sorted((sa[a],sa[bb])); f.write(f"{PAIRS.index((a2,b2))*4+phi[d]}\n")
        for b in range(18):
            a,i=divmod(b,3); f.write(f"{60+sa[a]*3+phi[i+1]-1}\n")
