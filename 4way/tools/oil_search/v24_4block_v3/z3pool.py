#!/usr/bin/env python3
"""z3: pick weeks from the Z2^2-invariant pool, coloured with 4 blocks (sizes from argv), so that every class
is covered once in exactly 3 of the 4 blocks.  usage: z3pool.py seed out.json [kinds]"""
import sys, json, itertools, random
from z3 import *
from pool import weeks_pool, classes
seed=int(sys.argv[1]); out=sys.argv[2]; kinds=tuple(sys.argv[3].split(",")) if len(sys.argv)>3 else ("RH","HHFF","RFF","HHH")
sizes=[6,6,6,5]
P=weeks_pool(kinds); CL=[classes(g) for _,g in P]
allc=sorted(set().union(*CL)); idx={c:i for i,c in enumerate(allc)}
print(len(P),"weeks",len(allc),"classes",flush=True)
y=[[Bool(f"y{w}_{c}") for c in range(4)] for w in range(len(P))]
z=[[Bool(f"z{k}_{c}") for c in range(4)] for k in range(len(allc))]
s=Solver(); s.set("random_seed",seed); 
by=[[] for _ in allc]
for w,cl in enumerate(CL):
    for c in cl: by[idx[c]].append(w)
for k in range(len(allc)):
    s.add(PbEq([(z[k][c],1) for c in range(4)],1))
    for c in range(4):
        s.add(PbEq([(y[w][c],1) for w in by[k]]+[(z[k][c],1)],1))
for c in range(4): s.add(PbEq([(y[w][c],1) for w in range(len(P))],sizes[c]))
r=s.check(); print(r,flush=True)
if r==sat:
    m=s.model(); res=[]
    for c in range(4):
        for w in range(len(P)):
            if is_true(m[y[w][c]]): res.append({"block":c,"kind":P[w][0],"groups":P[w][1]})
    json.dump(res,open(out,"w")); print("saved",out)
