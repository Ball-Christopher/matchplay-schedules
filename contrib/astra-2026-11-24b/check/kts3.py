import json,sys
from itertools import combinations
R=json.load(open(sys.argv[1]))
def prep(res):
    third={};cls={}
    for ci,c in enumerate(res):
        for t in c:
            cls[frozenset(t)]=ci
            for a,b in combinations(t,2):
                third[(a,b)]=third[(b,a)]=[x for x in t if x not in (a,b)][0]
    return third,cls
def iso(A,B):
    ta,ca=prep(A); tb,cb=prep(B)
    def close(m):
        m=dict(m); ch=True
        while ch:
            ch=False
            for a,b in combinations(list(m),2):
                c=ta[(a,b)]; d=tb[(m[a],m[b])]
                if c in m:
                    if m[c]!=d: return None
                else:
                    if d in m.values(): return None
                    m[c]=d; ch=True
        return m
    def ok(m):
        cm={}
        for t,ci in ca.items():
            img=frozenset(m[x] for x in t); cj=cb[img]
            if cm.setdefault(ci,cj)!=cj: return False
        return len(set(cm.values()))==7
    def rec(m):
        m=close(m)
        if m is None: return False
        if len(m)==15: return ok(m)
        a=min(x for x in range(15) if x not in m)
        for y in range(15):
            if y not in m.values():
                mm=dict(m); mm[a]=y
                if rec(mm): return True
        return False
    return rec({})
for i,j in combinations(range(7),2):
    r=iso(R[i],R[j])
    if r: print('ISOMORPHIC',i,j)
print('pairs checked; any isomorphic printed above')
