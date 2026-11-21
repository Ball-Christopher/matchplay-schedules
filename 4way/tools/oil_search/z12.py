import sys, itertools, time, json
from z3 import *
K=int(sys.argv[1]); sizes=list(map(int,sys.argv[2].split('+'))); tl=int(sys.argv[3]); seed=int(sys.argv[4]) if len(sys.argv)>4 else 0
v,n,W=12,3,11
blk=[b for b,sz in enumerate(sizes) for _ in range(sz)]
x=[[[Bool(f"x{w}_{p}_{g}") for g in range(n)] for p in range(v)] for w in range(W)]
s=Solver(); s.set("timeout",tl*1000); s.set("random_seed",seed)
for w in range(W):
    for p in range(v): s.add(PbEq([(x[w][p][g],1) for g in range(n)],1))
    for g in range(n): s.add(PbEq([(x[w][p][g],1) for p in range(v)],4))
    s.add(x[w][0][0])
for p in range(v): s.add(x[0][p][p//4])
ys=[]
for a,b in itertools.combinations(range(v),2):
    m=[]
    for w in range(W):
        mv=Bool(f"m{w}_{a}_{b}")
        for g in range(n): s.add(Or(Not(x[w][a][g]),Not(x[w][b][g]),mv))
        m.append(mv)
    s.add(PbEq([(mv,1) for mv in m],3))
    for k in range(len(sizes)):
        y=Bool(f"y{k}_{a}_{b}"); s.add(Or(Not(y),*[m[w] for w in range(W) if blk[w]==k])); ys.append(y)
s.add(PbGe([(y,1) for y in ys],198-K))
t=time.time(); r=s.check(); print(K,sizes,r,f"{time.time()-t:.0f}s",flush=True)
if r==sat:
    mo=s.model(); out=[]
    for w in range(W):
        wk=[]
        for g in range(n): wk+= [p+1 for p in range(v) if is_true(mo[x[w][p][g]])]
        out.append(wk)
    json.dump(out,open(f"z12_{sys.argv[2]}_{K}_{seed}.json","w")); print(out)
