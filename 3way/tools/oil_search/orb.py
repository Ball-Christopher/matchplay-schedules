# generic: point perm g (cycle type given), week orbits [(len, block)], solve with z3
import sys, json, itertools, time
from z3 import *
def solve(v, cycles, worbits, timeout=600, seed=0):
    g=list(range(v)); 
    pos=0
    for L in cycles:
        for i in range(L): g[pos+i]=pos+(i+1)%L
        pos+=L
    assert pos==v
    def powmap(k):
        m=list(range(v))
        for _ in range(k): m=[g[x] for x in m]
        return m
    order=1
    while powmap(order)!=list(range(v)): order+=1
    P=[powmap(k) for k in range(order)]
    T=list(itertools.combinations(range(v),3))
    def img(t,k): return tuple(sorted(P[k%order][x] for x in t))
    X=[]  # per orbit: dict triple->var
    for o,(L,b) in enumerate(worbits):
        assert order%L==0
        d={}
        for t in T:
            if t in d: continue
            orb=set(); u=t
            while u not in orb: orb.add(u); u=img(u,L)
            # triple orbit under g^L must be disjoint triples (else can't be in a week)
            ok=all(not(set(a)&set(c)) for a,c in itertools.combinations(orb,2))
            var=Bool(f"x{o}_{t}") if ok else None
            for u in orb: d[u]=var
        X.append(d)
    s=SolverFor("QF_FD"); s.set("timeout",timeout*1000); s.set("random_seed",seed)
    bypt=[[t for t in T if p in t] for p in range(v)]
    for o in range(len(worbits)):
        for p in range(v):
            lits=[X[o][t] for t in bypt[p] if X[o][t] is not None]
            lits=list({l.get_id():l for l in lits}.values())
            if not lits: print('trivially unsat',file=sys.stderr); return None
            s.add(PbEq([(l,1) for l in lits],1))
    nb=max(b for _,b in worbits)+1
    seen=set()
    for e in itertools.combinations(range(v),2):
        if e in seen: continue
        for k in range(order): seen.add(tuple(sorted((P[k][e[0]],P[k][e[1]]))))
        byb=[[] for _ in range(nb)]
        for o,(L,b) in enumerate(worbits):
            for j in range(L):
                # week j = g^j(week0); triple t in week j iff g^-j t in week 0
                for p in range(v):
                    if p in e: continue
                    t=tuple(sorted(e+(p,)))
                    var=X[o][img(t,order-j)]
                    if var is not None: byb[b].append(var)
        for b in range(nb): s.add(AtMost(*byb[b],1)) if len(byb[b])>1 else None
        for b1,b2 in itertools.combinations(range(nb),2): s.add(Or(byb[b1]+byb[b2]))
    t0=time.time(); r=s.check(); print(r, round(time.time()-t0,1), file=sys.stderr)
    if r!=sat: return None
    m=s.model(); weeks=[]; blocks=[]
    for o,(L,b) in enumerate(worbits):
        w0=sorted(set(t for t in T if X[o][t] is not None and is_true(m[X[o][t]])))
        for j in range(L):
            weeks.append(sorted(img(t,j) for t in w0)); blocks.append(b)
    return weeks, blocks
if __name__=="__main__":
    v=int(sys.argv[1]); cycles=json.loads(sys.argv[2]); wo=json.loads(sys.argv[3]); out=sys.argv[4]
    r=solve(v,cycles,[tuple(x) for x in wo],int(sys.argv[5]) if len(sys.argv)>5 else 600)
    if r: json.dump({"weeks":r[0],"blocks":r[1]},open(out,"w")); print("FOUND",out)
