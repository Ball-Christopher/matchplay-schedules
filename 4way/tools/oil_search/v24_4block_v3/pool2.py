#!/usr/bin/env python3
"""Extended pool for designs invariant under N = Z2^2 (N fixes every oil block):
 - single weeks invariant under all of N (pool.py), weight 1;
 - 'double weeks' {W, tau_j W}: W invariant under tau_i only (i=1,2,3), weight 2.  W is a partition of the 12
   tau_i-dyads into fixed groups (two dyads from different super-points) and quads (one point from each of 4
   dyads on 4 distinct super-points, standing for g and tau_i g).  W u tau_j W covers whole N-classes, each once,
   iff W's class list has no repeat.
Output: mask file 'kind weight lo hi' and a groups file (first week of each item, 24 points).  Deduplicated by mask."""
import sys, itertools
from pool import weeks_pool, classes
from mkmask import bit
PAIRS=[(x,y) for x in range(6) for y in range(x+1,6)]
def cbit(a,b,d):
    if a>b: a,b=b,a
    return 1<<(PAIRS.index((a,b))*4+d)
def ibit(a,i): return 1<<(60+a*3+i-1)
def doubles(i):
    j=[k for k in (1,2,3) if k!=i][0]
    dy=[(a,s) for a in range(6) for s in (0,1)]            # dyad (a,s): points 4a+{r, r^i}, r = 0 or j
    rep=lambda a,s:(0 if s==0 else j)
    out={}
    def rec(used,mask,groups):
        if len(used)==12:
            if mask not in out: out[mask]=list(groups)
            return
        d0=next(d for d in dy if d not in used); a,s=d0; x=rep(a,s)
        # fixed group with another dyad
        for d1 in dy:
            if d1 in used or d1[0]==a or d1<=d0: continue
            b,t=d1; y=rep(b,t)
            m=ibit(a,i)|ibit(b,i)|cbit(a,b,x^y)|cbit(a,b,x^y^i)
            if m&mask or bin(m).count("1")!=4: continue
            rec(used|{d0,d1},mask|m,groups+[(4*a+x,4*a+(x^i),4*b+y,4*b+(y^i))])
        # quad
        others=[d for d in dy if d not in used and d[0]!=a and d>d0]
        for tr in itertools.combinations(others,3):
            if len({d[0] for d in tr})<3: continue
            for fl in itertools.product((0,1),repeat=3):
                pts=[4*a+x]+[4*b+(rep(b,t)^(i if f else 0)) for (b,t),f in zip(tr,fl)]
                m=0; ok=True
                for p,q in itertools.combinations(pts,2):
                    bt=cbit(p//4,q//4,(p&3)^(q&3))
                    if bt&m or bt&mask: ok=False;break
                    m|=bt
                if not ok: continue
                g=tuple(pts); g2=tuple((p&~3)|((p&3)^i) for p in pts)
                rec(used|{d0}|set(tr),mask|m,groups+[g,g2])
    rec(frozenset(),0,[])
    return out
if __name__=="__main__":
    pre=sys.argv[1]
    items=[]
    for k,g in weeks_pool():
        m=0
        for c in classes(g):
            b,h=bit(c); m|=1<<(b+60*h)
        items.append((k,1,m,sum(map(list,g),[])))
    for i in (1,2,3):
        d=doubles(i); print("type",i,len(d),flush=True)
        for m,g in d.items(): items.append((f"D{i}",2,m,sum(map(list,g),[])))
    with open(pre+".mask","w") as f, open(pre+".groups","w") as fg:
        f.write(f"{len(items)}\n")
        for k,w,m,g in items:
            f.write(f"{k} {w} {m&((1<<60)-1)} {m>>60}\n"); fg.write(" ".join(map(str,g))+"\n")
