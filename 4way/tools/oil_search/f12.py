import json, random, itertools, sys
from finish import *
from p12 import best, load
from l12 import lanes12
r=json.load(open("p12.json"))
cands=[f for a,b,f in r if b[0]==27 and a[0]==40]+[f for a,b,f in r if b[0]==27 and a[0]!=40]
rng=random.Random(3);res=[]
for f in cands:
    W0=load(f);W=[[w[i:i+4] for i in range(0,12,4)] for w in W0]
    x=lanes12(W,rng)
    if x is None:continue
    exc,Wl=x;rp,parts=best(W0,(3,3,3,2));print(f,"exc",exc,"3blk",best(W0,(4,4,3))[0],flush=True)
    res.append((exc,f,parts,Wl))
    if len(res)>=4 or exc==0:break
res.sort(key=lambda t:t[0]);exc,f,parts,Wl=res[0]
blks=[[Wl[i] for i in b] for b in parts]
finish("v12_oil",12,blks,"Resolvable 2-(12,4,3) design from the annealed pool (%s); weeks partitioned exhaustively into 3+3+3+2 oil blocks minimising same-block repeat meetings; lane pairs by DFS over group order within weeks (1 bowler one off); block/week order annealed for prefix spread; positions by de Werra (positions.assign)."%f.split('/')[-1],rng,steps=30000)
