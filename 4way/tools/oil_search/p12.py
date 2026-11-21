import json, itertools, glob, sys
from collections import Counter
def load(f):
    if f.endswith('.json'): return json.load(open(f))["weeks"]
    return [list(map(int,l.split())) for l in open(f) if l.strip()]
def best(W,sizes):
    r=len(W); cps=[[frozenset(c) for i in range(0,12,4) for c in itertools.combinations(w[i:i+4],2)] for w in W]
    cache={}
    def rep(b):
        if b not in cache:
            c=Counter(x for i in b for x in cps[i]); cache[b]=sum(n-1 for n in c.values())
        return cache[b]
    bestv=(999,None)
    def rec(rest,sz,acc,parts):
        nonlocal bestv
        if acc>=bestv[0]: return
        if not sz: bestv=(acc,parts); return
        f=rest[0]
        for b in itertools.combinations(rest[1:],sz[0]-1):
            b=(f,)+b; rec([i for i in rest if i not in b],sz[1:],acc+rep(b),parts+[b])
    for perm in set(itertools.permutations(sizes)): rec(list(range(r)),list(perm),0,[])
    return bestv
if __name__=="__main__":
    files=sys.argv[1:]
    res=[]
    for f in files:
        try: W=load(f)
        except Exception as e: continue
        if len(W)!=11 or any(len(w)!=12 for w in W): continue
        res.append((best(W,(4,4,3)),best(W,(3,3,3,2)),f))
    res.sort(key=lambda t:t[0][0]); print("3blk best:",[(a[0],f.split('/')[-1]) for a,b,f in res[:5]])
    res.sort(key=lambda t:t[1][0]); print("4blk best:",[(b[0],f.split('/')[-1]) for a,b,f in res[:5]])
    json.dump([(a,b,f) for a,b,f in res],open("p12.json","w"))
    
