import json,sys,itertools,collections
d=json.load(open(sys.argv[1]));W=d["weeks"];v=d["players"];n=v//4;r=v-1
assert len(W)==r
pc=collections.Counter();lc=collections.Counter();spread=[]
for w in W:
    assert sorted(w)==list(range(1,v+1)),"week not a partition"
    for L in range(n):
        g=w[4*L:4*L+4]
        for p in g: lc[p,L]+=1
        for a,b in itertools.combinations(sorted(g),2): pc[a,b]+=1
    vals=[pc[a,b] for a,b in itertools.combinations(range(1,v+1),2)]
    spread.append(max(vals)-min(vals))
print("file",sys.argv[1]);print("weeks",len(W),"each a partition of 1..%d: OK"%v)
print("pair counts: pairs=%d min=%d max=%d"%(len(pc),min(pc.values()),max(pc.values())))
assert len(pc)==v*(v-1)//2 and set(pc.values())=={3}
prof=collections.Counter(tuple(sorted(lc[p,L] for L in range(n))) for p in range(1,v+1))
print("lane profiles per bowler:",dict(prof))
lo,hi=r//n,-(-r//n)
assert all(lo<=lc[p,L]<=hi for p in range(1,v+1) for L in range(n))
print("prefix spread by week:",spread,"max",max(spread))
print("distinct weeks (as sets of groups):",len({frozenset(frozenset(w[4*L:4*L+4]) for L in range(n)) for w in W}))
print("VALID: resolvable 2-(%d,4,3), exact lane balance (%d..%d per lane pair)"%(v,lo,hi))
