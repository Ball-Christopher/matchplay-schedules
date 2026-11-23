#!/usr/bin/env python3
"""Final assembly of 4way/v24_oil from design_eq16_lanes.txt (23 weeks, groups already in lane-pair order,
blocks 6+6+6+5): re-verify everything from the weeks alone, order blocks/weeks for prefix spread (blocks stay
contiguous), assign positions (tools/positions.py), write the .json/.toml in the library format."""
import json, itertools, random, math, sys
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[3]/"tools"))
from positions import assign
OUT=HERE.parents[2]
rows=[list(map(int,l.split())) for l in open(HERE/"design_eq16_lanes.txt")]
W=[[[p+1 for p in r[i:i+4]] for i in range(0,24,4)] for r in rows]
blks=[W[0:6],W[6:12],W[12:18],W[18:23]]
v=24
def spreads(W):
    m=Counter();out=[];cp=list(itertools.combinations(range(1,v+1),2))
    for wk in W:
        for g in wk:
            for a,b in itertools.combinations(sorted(g),2): m[(a,b)]+=1
        vals=[m[c] for c in cp]; out.append(max(vals)-min(vals))
    return out,m
def reps(W,blocks):
    tot=0;i=0
    for b in blocks:
        c=Counter(frozenset(p) for wk in W[i:i+b] for g in wk for p in itertools.combinations(g,2)); tot+=sum(n-1 for n in c.values()); i+=b
    return tot
def lane_off(W):
    c=Counter()
    for wk in W:
        for l,g in enumerate(wk):
            for p in g:c[(p,l)]+=1
    return sum(1 for p in range(1,v+1) if any(not 3<=c[(p,l)]<=4 for l in range(6))),c
rng=random.Random(1)
flat=lambda b:[w for x in b for w in x]
def cost(b):
    s=spreads(flat(b))[0]; return max(s[:-1])*1000+sum(x*x for x in s)
cur=cost(blks); best=(cur,[list(b) for b in blks]); T=30
for it in range(4000):
    nb=[list(b) for b in blks]
    if rng.random()<0.3: i,j=rng.sample(range(4),2); nb[i],nb[j]=nb[j],nb[i]
    else:
        b=rng.choice(nb); i,j=rng.sample(range(len(b)),2); b[i],b[j]=b[j],b[i]
    n=cost(nb)
    if n<=cur or rng.random()<math.exp((cur-n)/T):
        blks=nb; cur=n
        if cur<best[0]: best=(cur,[list(b) for b in blks])
    T=max(0.5,T*0.998)
blks=best[1]
W=flat(blks); blocks=[len(b) for b in blks]
W=assign(W,4)
assert all(sorted(p for g in wk for p in g)==list(range(1,v+1)) for wk in W)
sp,m=spreads(W); assert set(m.values())=={3} and len(m)==276
rp=reps(W,blocks); off,lc=lane_off(W)
assert rp==0 and off==0 and len({tuple(sorted(tuple(sorted(g)) for g in wk)) for wk in W})==23
# positions: floor/ceil overall and within one of even after every week
pc=Counter()
for wk in W:
    for g in wk:
        for q,p in enumerate(g): pc[(p,q)]+=1
    assert all(max(pc[(p,q)] for q in range(4))-min(pc[(p,q)] for q in range(4))<=1 for p in range(1,v+1))
method=("Design invariant under Z2^2 x Z3 (two orbits of 12 bowlers). Z2^2 fixes every oil block: each week is either fixed by "
 "all of Z2^2 or is one of a pair {W, tW} with W fixed by one involution, so a week's couples are whole Z2^2-classes (78 classes) "
 "and the design is an exact cover of classes by 380,000 candidate weeks/week-pairs. Z3 cycles the three 6-week blocks and fixes "
 "each week of the 5-week block; an exhaustive class-cover DFS (asearch.c) found block 1 given the 5-week block. Z3 also rotates "
 "the lane pairs in two tracks of three (lanes_eq.c, annealing over block 1's group orders and 18 choices per week of block 4). "
 "4 clash-free blocks 6+6+6+5 (the lower bound); the disjoint leaves force prefix spread <= 2 for any week order; positions by "
 "de Werra (positions.assign).")
flatw=[[p for g in wk for p in g] for wk in W]
d={"players":v,"group":4,"rounds":1,"lambda":3,"weeks":flatw,"blocks":blocks,"block_repeats":rp,"lane_balance_exact":off==0,"method":method}
if "--write" in sys.argv:
    json.dump(d,open(OUT/"v24_oil.json","w"),indent=1)
    hdr=f"# {v} players, 4 per lane pair, {v-1} weeks: every couple meets exactly 3 times.\n# Oil-pattern blocks (consecutive weeks): {' + '.join(map(str,blocks))} = {v-1} weeks.\n"
    i=1
    for k,b in enumerate(blocks): hdr+=f"#   block {k+1}: weeks {i}-{i+b-1}\n"; i+=b
    hdr+=f"# Same-block repeat meetings: {rp} (no couple meets twice on one pattern; every couple meets on 3 different patterns).\n"
    hdr+="# Lane pairs: exact (floor/ceil for every bowler). Groups in lane-pair order; within a group: left lane 1st, right lane 1st, left lane 2nd, right lane 2nd.\n"
    open(OUT/"v24_oil.toml","w").write(hdr+"[schedule]\nweeks = [\n"+"".join("  "+json.dumps(w)+",\n" for w in flatw)+"]\n")
json.dump(d,open(HERE/"final_v24_oil.json","w"),indent=1)
print("blocks",blocks,"repeats",rp,"lane off",off,"lane counts",sorted(Counter(lc.values()).items()),"prefix",sp,"worst",max(sp[:-1]))
