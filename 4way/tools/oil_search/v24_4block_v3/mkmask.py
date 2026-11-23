#!/usr/bin/env python3
"""Class masks of the pool weeks: 60 cross classes (bits 0..59 of lo), 18 inner classes (bits 0..17 of hi)."""
import sys
from pool import weeks_pool, classes
def bit(c):
    if c[0]=="c":
        _,a,b,d=c; pi=[(x,y) for x in range(6) for y in range(x+1,6)].index((a,b)); return (pi*4+d,0)
    _,a,i=c; return (a*3+i-1,1)
if __name__=="__main__":
  P=weeks_pool()
  with open(sys.argv[1],"w") as f:
    f.write(f"{len(P)}\n")
    for k,g in P:
        lo=hi=0
        for c in classes(g):
            b,h=bit(c)
            if h: hi|=1<<b
            else: lo|=1<<b
        f.write(f"{k} {lo} {hi}\n")
  for v in (0,1):
    phi=[0,1,2,3] if v==0 else [0,2,3,1]
    sa=[1,2,0,4,5,3]
    with open(sys.argv[1]+f".sig{v}","w") as f:
        for h in (0,1):
            for b in range(60 if h==0 else 18):
                if h==0:
                    pi,d=divmod(b,4); a,bb=[(x,y) for x in range(6) for y in range(x+1,6)][pi]
                    a2,b2=sa[a],sa[bb]; c=("c",min(a2,b2),max(a2,b2),phi[d])
                else:
                    a,i=divmod(b,3); c=("i",sa[a],phi[i+1])
                nb,nh=bit(c); assert nh==h
                f.write(f"{nb}\n")
