#!/usr/bin/env python3
"""Write the exact-cover instance for dlx.c: items (class,colour) and miss(class); options week@colour and miss(class,colour)."""
import sys
from pool import weeks_pool, classes
kinds=tuple(sys.argv[2].split(",")) if len(sys.argv)>2 else ("RH","HHFF","RFF","HHH")
P=weeks_pool(kinds); CL=[classes(g) for _,g in P]
allc=sorted(set().union(*CL)); idx={c:i for i,c in enumerate(allc)}; K=len(allc)
with open(sys.argv[1],"w") as f:
    f.write(f"{5*K} {len(P)*4+4*K} {len(P)}\n")
    for w,cl in enumerate(CL):
        for c in range(4): f.write(f"{w} {c} "+" ".join(str(4*idx[x]+c) for x in sorted(cl))+"\n")
    for k in range(K):
        for c in range(4): f.write(f"-1 {c} {4*k+c} {4*K+k}\n")
