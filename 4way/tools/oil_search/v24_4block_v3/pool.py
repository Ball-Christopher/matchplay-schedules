#!/usr/bin/env python3
"""Pool of weeks invariant under N = Z2^2 acting semiregularly on 24 points.
Point = 4*a + u, a in 0..5 (super-point = N-orbit), u in 0..3 (element of Z2^2, xor).
Group types: F (a whole N-orbit), H (type i, two tau_i-dyads from two super-points, an N-orbit of 2 groups),
R (one point from each of 4 super-points, an N-orbit of 4 groups).
A week's pairs are unions of classes: cross class (a,b,d): pairs {4a+u, 4b+(u^d)}; inner class (a,i): pairs {4a+u,4a+(u^i)}.
"""
import itertools
def weeks_pool(kinds=("RH","HHFF","RFF","HHH")):
    pool=[]  # (kind, groups(list of 4-tuples of points))
    def F(a): return [tuple(4*a+u for u in range(4))]
    def H(a,b,i,d):  # d in coset rep: classes d and d^i
        g=(4*a,4*a+i,4*b+d,4*b+(d^i)); j=[k for k in (1,2,3) if k!=i][0]; return [g,tuple((p&~3)|((p&3)^j) for p in g)]
    def R(sp,us):
        g=tuple(4*a+u for a,u in zip(sp,us)); return [tuple((p&~3)|((p&3)^n) for p in g) for n in range(4)]
    Hopts=lambda a,b:[H(a,b,i,d) for i in (1,2,3) for d in ([0,[k for k in (1,2,3) if k!=i][0]])]
    Ropts=lambda sp:[R(sp,(0,)+us) for us in itertools.product(range(4),repeat=3)]
    S=range(6)
    for a,b in itertools.combinations(S,2):
        rest=[x for x in S if x not in (a,b)]
        if "RH" in kinds:
            for h in Hopts(a,b):
                for r in Ropts(rest): pool.append(("RH",h+r))
        if "RFF" in kinds:
            for r in Ropts(rest): pool.append(("RFF",F(a)+F(b)+r))
        if "HHFF" in kinds:
            c=rest[0]
            for d in rest[1:]:
                e,f=[x for x in rest if x not in (c,d)]
                for h1 in Hopts(c,d):
                    for h2 in Hopts(e,f): pool.append(("HHFF",F(a)+F(b)+h1+h2))
    if "HHH" in kinds:
        def matchings(l):
            if not l: yield []; return
            a=l[0]
            for b in l[1:]:
                for m in matchings([x for x in l if x not in (a,b)]): yield [(a,b)]+m
        for m in matchings(list(S)):
            for hs in itertools.product(*[Hopts(a,b) for a,b in m]): pool.append(("HHH",sum(hs,[])))
    return pool
def classes(groups):
    cl=set()
    for g in groups:
        for p,q in itertools.combinations(sorted(g),2):
            a,b=p//4,q//4
            cl.add(("c",a,b,(p&3)^(q&3)) if a!=b else ("i",a,(p&3)^(q&3)))
    return cl
if __name__=="__main__":
    P=weeks_pool(); print(len(P))
    from collections import Counter
    print(Counter(k for k,_ in P))
    for k,g in P:
        assert sorted(sum(map(list,g),[]))==list(range(24)),(k,g)
        n=len(classes(g)); assert sum(4 if c[0]=="c" else 2 for c in classes(g))==36,(k,g,n)
    print("ok")
