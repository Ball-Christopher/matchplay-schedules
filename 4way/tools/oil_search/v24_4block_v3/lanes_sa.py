#!/usr/bin/env python3
"""Lane pairs by annealing over the group order in each week (swap two lane pairs in one week).
usage: lanes_sa.py design.json out.json [seed] [iters]"""
import sys, json, random, math
d=json.load(open(sys.argv[1])); seed=int(sys.argv[3]) if len(sys.argv)>3 else 0; IT=int(sys.argv[4]) if len(sys.argv)>4 else 3000000
random.seed(seed)
weeks=[[list(g) for g in w] for b in d["blocks"] for w in b]; sizes=[len(b) for b in d["blocks"]]; W=len(weeks)
for w in weeks: random.shuffle(w)
cnt=[[0]*6 for _ in range(24)]
for w in weeks:
    for l,g in enumerate(w):
        for p in g: cnt[p][l]+=1
pen=lambda c:(3-c if c<3 else (c-4 if c>4 else 0))
cost=sum(pen(c) for r in cnt for c in r); best=cost
for it in range(IT):
    if cost==0: break
    T=0.6*(0.15/0.6)**(it/IT)
    w=random.randrange(W); a,b=random.sample(range(6),2); ga,gb=weeks[w][a],weeks[w][b]
    dl=0
    for p in ga: dl+=pen(cnt[p][a]-1)-pen(cnt[p][a])+pen(cnt[p][b]+1)-pen(cnt[p][b])
    for p in gb: dl+=pen(cnt[p][b]-1)-pen(cnt[p][b])+pen(cnt[p][a]+1)-pen(cnt[p][a])
    if dl<=0 or random.random()<math.exp(-dl/T):
        for p in ga: cnt[p][a]-=1; cnt[p][b]+=1
        for p in gb: cnt[p][b]-=1; cnt[p][a]+=1
        weeks[w][a],weeks[w][b]=gb,ga; cost+=dl
        if cost<best: best=cost
print(sys.argv[1],"lane cost",cost,"best",best,flush=True)
if cost==0: json.dump({"weeks":weeks,"sizes":sizes},open(sys.argv[2],"w"))
