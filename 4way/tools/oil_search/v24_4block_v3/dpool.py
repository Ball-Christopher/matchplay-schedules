#!/usr/bin/env python3
"""Candidate fourth blocks D that are sigma-invariant as sets of weeks (so that sigma can also rotate the lanes):
weight-5 clash-free unions of sigma-invariant pool items (singles w1, doubles w2) and sigma-orbits of singles (w3).
usage: dpool.py poolprefix sigvariant out   -> lines: Xlo Xhi | item ids (orbit items as three ids o:a,b,c)"""
import sys, itertools
pre,v,out=sys.argv[1],int(sys.argv[2]),sys.argv[3]
L=[l.split() for l in open(pre+".mask").read().split("\n")[1:] if l]
kinds=[l[0] for l in L]; wt=[int(l[1]) for l in L]; msk=[int(l[2])|(int(l[3])<<60) for l in L]
sg=[int(x) for x in open(f"{pre}.sig{v}")]
def ap(m):
    r=0
    while m:
        b=m&-m; r|=1<<sg[b.bit_length()-1]; m^=b
    return r
idx={}
for i,m in enumerate(msk): idx.setdefault(m,i)
items=[]  # (weight, mask, ids)
for i,m in enumerate(msk):
    if ap(m)==m: items.append((wt[i],m,(i,)))
ninv=len(items)
for i,m in enumerate(msk):
    if wt[i]!=1: continue
    m1=ap(m); m2=ap(m1)
    if m1==m or (m&m1) or (m&m2) or (m1&m2): continue
    j,k=idx[m1],idx[m2]
    if i<j and i<k: items.append((3,m|m1|m2,(i,j,k)))
print("invariant items",ninv,"by kind",{k:sum(1 for w,m,ids in items[:ninv] if kinds[ids[0]]==k) for k in set(kinds)},"orbit items",len(items)-ninv,flush=True)
res=[]
def rec(start,w,m,ids):
    if w==5: res.append((m,ids)); return
    for t in range(start,len(items)):
        ww,mm,ii=items[t]
        if w+ww<=5 and not (mm&m): rec(t+1,w+ww,m|mm,ids+[ii])
rec(0,0,0,[])
print("D candidates",len(res),"distinct X",len({m for m,_ in res}))
with open(out,"w") as f:
    for m,ids in res: f.write(f"{m&((1<<60)-1)} {m>>60} | "+" ; ".join(",".join(map(str,i)) for i in ids)+"\n")
