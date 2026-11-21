import json,time,itertools
from z3 import *
reps=json.load(open('k15_reps.json'))
def z3check(K):
    s=Solver(); x=[[[Bool(f'x{w}_{t}_{l}') for l in range(5)] for t in range(5)] for w in range(7)]
    for w in range(7):
        for t in range(5): s.add(PbEq([(x[w][t][l],1) for l in range(5)],1))
        for l in range(5): s.add(PbEq([(x[w][t][l],1) for t in range(5)],1))
    for t in range(5): s.add(x[0][t][t])   # WLOG
    for b in range(15):
        for l in range(5):
            lits=[(x[w][t][l],1) for w in range(7) for t in range(5) if b in K[w][t]]
            s.add(PbGe(lits,1)); s.add(PbLe(lits,2))
    return str(s.check())
def dfscheck(K):
    """independent exhaustive DFS; returns (found, nodes)"""
    cnt=[[0]*5 for _ in range(15)]; nodes=0
    for t in range(5):
        for b in K[0][t]: cnt[b][t]=1
    def week(w):
        nonlocal nodes
        if w==7: return all(1<=c<=2 for r in cnt for c in r)
        rem=7-w
        if any(sum(1 for c in r if c==0)>rem for r in cnt): return False
        def grp(t,used):
            nonlocal nodes
            nodes+=1
            if t==5: return week(w+1)
            for l in range(5):
                if used>>l&1 or any(cnt[b][l]>=2 for b in K[w][t]): continue
                for b in K[w][t]: cnt[b][l]+=1
                r=grp(t+1,used|1<<l)
                for b in K[w][t]: cnt[b][l]-=1
                if r: return True
            return False
        return grp(0,0)
    return week(1),nodes
for i,K in enumerate(reps):
    # sanity: it is a KTS(15)
    pairs=set()
    for W in K:
        assert sorted(p for T in W for p in T)==list(range(15))
        for T in W:
            for a,b in itertools.combinations(sorted(T),2): assert (a,b) not in pairs; pairs.add((a,b))
    assert len(pairs)==105
    t=time.time(); z=z3check(K); tz=time.time()-t
    t=time.time(); f,n=dfscheck(K); td=time.time()-t
    print(f'KTS(15) #{i+1}: valid KTS; z3 exact lane balance: {z} ({tz:.2f}s); exhaustive DFS: {"FOUND" if f else "none"} ({n} nodes, {td:.1f}s)')
