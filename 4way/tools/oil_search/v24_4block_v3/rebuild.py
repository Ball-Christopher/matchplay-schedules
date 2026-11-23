#!/usr/bin/env python3
"""Rebuild full 23-week designs from sigsearch FOUND lines and check them from scratch.
usage: rebuild.py poolprefix sigvariant foundfile outprefix"""
import sys, json, itertools
from collections import Counter
pre,v,ff,outp=sys.argv[1],int(sys.argv[2]),sys.argv[3],sys.argv[4]
V=[([1,2,0,4,5,3],[0,1,2,3]),([1,2,0,4,5,3],[0,2,3,1]),([1,2,0,3,4,5],[0,1,2,3]),([1,2,0,3,4,5],[0,2,3,1])]
sa,phi=V[v]; sig=lambda p:4*sa[p//4]+phi[p&3]
kinds=[l.split()[0] for l in open(pre+".mask").read().split("\n")[1:] if l]
groups=[list(map(int,l.split())) for l in open(pre+".groups")]
def weeks_of(it):
    w=[groups[it][i:i+4] for i in range(0,24,4)]
    if kinds[it].startswith("D"):
        i=int(kinds[it][1]); j=[k for k in (1,2,3) if k!=i][0]
        return [w,[[ (p&~3)|((p&3)^j) for p in g] for g in w]]
    return [w]
def check(blocks):
    tot=Counter()
    for b in blocks:
        c=Counter()
        for w in b:
            assert sorted(sum(w,[]))==list(range(24))
            for g in w:
                for pr in itertools.combinations(sorted(g),2): c[pr]+=1
        if max(c.values())>1: return "clash"
        tot.update(c)
    if len(tot)!=276 or set(tot.values())!={3}: return "balance"
    return "ok"
n=0
for line in open(ff):
    a,d=line.split("A:")[1].split("D:"); A=sum((weeks_of(int(x)) for x in a.split()),[]); D=sum((weeks_of(int(x)) for x in d.split()),[])
    ap=lambda W,k:[[[(sig(p) if k==1 else sig(sig(p))) for p in g] for g in w] for w in W]
    blocks=[A,ap(A,1),ap(A,2),D]
    r=check(blocks); nd=len({tuple(sorted(tuple(sorted(g)) for g in w)) for b in blocks for w in b})
    print(n,[len(b) for b in blocks],r,"distinct weeks",nd,"A kinds",[kinds[int(x)] for x in a.split()],"D kinds",[kinds[int(x)] for x in d.split()])
    if r=="ok": json.dump({"blocks":blocks},open(f"{outp}_{n}.json","w"))
    n+=1
