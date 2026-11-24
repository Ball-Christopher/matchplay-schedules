import json,sys
from itertools import combinations
import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from checkm import greedy,groups,repo_first
cases=[(24,3,'oil'),(24,3,'main'),(24,4,'oil'),(24,4,'main'),(30,3,'oil'),(30,3,'main'),(32,4,'oil'),(32,4,'main'),(36,3,'oil'),(36,3,'main'),(36,4,'oil'),(36,4,'main')]
def eligible(v,k,tail):
    used={frozenset(p) for w in tail for g in groups(w,k) for p in combinations(g,2)}
    return [q for q in combinations(range(1,v+1),k) if not any(frozenset(p) in used for p in combinations(q,2))]
def weeks_from(v,k,cands):
    # all partitions of 1..v into groups from cands (exact cover), yields sets of groups
    by={x:[q for q in cands if q[0]==x] for x in range(1,v+1)}
    out=[]
    def rec(left,chosen):
        if not left: out.append(list(chosen)); return
        x=min(left)
        for q in by[x]:
            if all(y in left for y in q):
                chosen.append(q); rec(left-set(q),chosen); chosen.pop()
    rec(set(range(1,v+1)),[]); return out
for v,k,w in cases:
    W=repo_first(v,k,w); g=greedy(W,k); L=(v-1)//(k-1); r=len(W); t=g[-1]
    lb=len(g)-1+-(-(t+r)//L)
    extra=''
    if (v,k) in [(24,4),(32,4)]:
        tail=W[-t:]; el=eligible(v,k,tail)
        extra=f" tail {t}, eligible groups {len(el)}"
        if len(el)>=v//k:
            wk=weeks_from(v,k,el)
            # pairs of compatible weeks (sharing no couple)
            P=[{frozenset(p) for q in x for p in combinations(q,2)} for x in wk]
            two=sum(1 for i in range(len(P)) for j in range(i+1,len(P)) if not P[i]&P[j])
            extra+=f", one-week continuations {len(wk)}, couple-disjoint two-week continuations {two}"
            if two==0:
                lb2=len(g)-1+1+-(-(r-1)//L) if wk else None
                extra+=f" => with <=1 extra week: {len(g)-1}+1+ceil({r}-1/{L}) = {lb2}"
        else:
            extra+=f" < {v//k} needed: forced cut => {len(g)}+ceil({r}/{L}) = {len(g)+-(-r//L)}"
    print(f"{k}w{v} {w}: r1 blocks {g} L={L} simple LB={lb}{extra}")
