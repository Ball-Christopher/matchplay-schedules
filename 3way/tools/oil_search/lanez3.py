import sys, json, time
from z3 import *
src,v,out,seed=sys.argv[1],int(sys.argv[2]),sys.argv[3],int(sys.argv[4])
weeks=json.load(open(src))["weeks"]; n=v//3; r=len(weeks); lo,hi=r//n,-(-r//n)
s=SolverFor("QF_FD"); s.set("timeout",900000); s.set("random_seed",seed)
y=[[[Bool(f"y{w}_{g}_{l}") for l in range(n)] for g in range(n)] for w in range(r)]
for w in range(r):
    for g in range(n): s.add(PbEq([(y[w][g][l],1) for l in range(n)],1))
    for l in range(n): s.add(PbEq([(y[w][g][l],1) for g in range(n)],1))
for g in range(n): s.add(y[0][g][g])
for p in range(v):
    gi=[next(g for g,t in enumerate(w) if p in t) for w in weeks]
    for l in range(n):
        lits=[y[w][gi[w]][l] for w in range(r)]
        s.add(AtMost(*lits,hi)); s.add(AtLeast(*lits,lo))
t0=time.time(); res=s.check(); print(res,time.time()-t0)
if res==sat:
    m=s.model(); W=[]
    for w in range(r):
        row=[None]*n
        for g in range(n):
            for l in range(n):
                if is_true(m[y[w][g][l]]): row[l]=weeks[w][g]
        W.append(row)
    json.dump(W,open(out,"w")); print("FOUND")
