#!/usr/bin/env python3
"""Exact lane pairs by z3: order the 6 groups of every week so that every bowler is on every lane pair 3 or 4 times.
usage: lanes_z3.py design.json out.json [timeout_s] [seed]"""
import sys, json
from z3 import *
d=json.load(open(sys.argv[1])); to=int(sys.argv[3]) if len(sys.argv)>3 else 120; seed=int(sys.argv[4]) if len(sys.argv)>4 else 0
weeks=[w for b in d["blocks"] for w in b]; sizes=[len(b) for b in d["blocks"]]
W=len(weeks)
x=[[[Bool(f"x{w}_{g}_{l}") for l in range(6)] for g in range(6)] for w in range(W)]
s=Solver(); s.set("timeout",to*1000); s.set("random_seed",seed)
for w in range(W):
    for g in range(6): s.add(PbEq([(x[w][g][l],1) for l in range(6)],1))
    for l in range(6): s.add(PbEq([(x[w][g][l],1) for g in range(6)],1))
for l in range(6): s.add(x[0][l][l])
for p in range(24):
    where=[(w,g) for w in range(W) for g in range(6) if p in weeks[w][g]]
    for l in range(6):
        t=[(x[w][g][l],1) for w,g in where]
        s.add(PbGe(t,3)); s.add(PbLe(t,4))
r=s.check(); print(sys.argv[1],r,flush=True)
if r==sat:
    m=s.model(); out=[]
    for w in range(W):
        o=[None]*6
        for g in range(6):
            for l in range(6):
                if is_true(m[x[w][g][l]]): o[l]=weeks[w][g]
        out.append(o)
    json.dump({"weeks":out,"sizes":sizes},open(sys.argv[2],"w"))
