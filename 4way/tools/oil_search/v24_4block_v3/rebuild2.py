#!/usr/bin/env python3
"""Rebuild designs from runx logs (X line with D items => FOUND A lists); verify from scratch; require every D week
sigma-invariant.  Writes out/eq_<n>.txt (23 lines of 24 points: A, sA, ssA, D) and .json.  usage: rebuild2.py pre v logs..."""
import sys, json, itertools
from collections import Counter
pre,v=sys.argv[1],int(sys.argv[2])
V=[([1,2,0,4,5,3],[0,1,2,3]),([1,2,0,4,5,3],[0,2,3,1])]
sa,phi=V[v]; sig=lambda p:4*sa[p//4]+phi[p&3]
kinds=[l.split()[0] for l in open(pre+".mask").read().split("\n")[1:] if l]
groups=[list(map(int,l.split())) for l in open(pre+".groups")]
def weeks_of(it):
    w=[groups[it][i:i+4] for i in range(0,24,4)]
    if kinds[it].startswith("D"):
        i=int(kinds[it][1]); j=[k for k in (1,2,3) if k!=i][0]
        return [w,[[ (p&~3)|((p&3)^j) for p in g] for g in w]]
    return [w]
canon=lambda w:tuple(sorted(tuple(sorted(g)) for g in w))
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
    return "ok" if len(tot)==276 and set(tot.values())=={3} else "balance"
n=0
for fn in sys.argv[3:]:
    for line in open(fn):
        if "FOUND" not in line: continue
        head,tail=line.split("=>"); dids=[int(x) for part in head.split("|")[1].split(";") for x in part.split(",")]
        D=sum((weeks_of(i) for i in dids),[])
        dinv=all(canon([[sig(p) for p in g] for g in w])==canon(w) for w in D)
        for fa in tail.split("~"):
            if "FOUND" not in fa: continue
            A=sum((weeks_of(int(x)) for x in fa.split("A:")[1].split()),[])
            ap=lambda W,k:[[[(sig(p) if k==1 else sig(sig(p))) for p in g] for g in w] for w in W]
            blocks=[A,ap(A,1),ap(A,2),D]; r=check(blocks); nd=len({canon(w) for b in blocks for w in b})
            if n<5 or r!="ok" or not dinv: print(n,[len(b) for b in blocks],r,"distinct",nd,"D sigma-invariant",dinv)
            if r=="ok" and dinv and nd==23:
                json.dump({"blocks":blocks,"sigma_variant":v},open(f"out/eq_{n}.json","w"))
                with open(f"out/eq_{n}.txt","w") as o:
                    for b in blocks:
                        for w in b: o.write(" ".join(str(p) for g in w for p in g)+"\n")
                n+=1
print("designs written",n)
