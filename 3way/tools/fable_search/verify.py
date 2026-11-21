import json,sys,itertools,collections
def check(path, round1=None):
    d=json.load(open(path)); v=d['players']; lam=d['lambda']; W=d['weeks']; n=v//3; r=len(W)
    assert d['group']==3
    for w in W: assert sorted(w)==list(range(1,v+1)), 'not a permutation'
    pc=collections.Counter(); lc=[[0]*n for _ in range(v+1)]; trios=collections.Counter()
    for w in W:
        for g in range(n):
            t=w[3*g:3*g+3]; trios[frozenset(t)]+=1
            for a,b in itertools.combinations(sorted(t),2): pc[(a,b)]+=1
            for p in t: lc[p][g]+=1
    pairs_ok=all(pc[(a,b)]==lam for a in range(1,v+1) for b in range(a+1,v+1))
    lo,hi=r//n,-(-r//n)
    off=sum(1 for p in range(1,v+1) for g in range(n) if not lo<=lc[p][g]<=hi)
    print(f"{path.split('/')[-1]}: v={v} weeks={r} lane pairs={n} lambda={lam}")
    print(f"  every week a permutation: True; all {v*(v-1)//2} couples exactly {lam}x: {pairs_ok} (min {min(pc.values())}, max {max(pc.values())}, distinct {len(pc)})")
    print(f"  lane counts allowed {lo}..{hi}: observed {sorted(set(x for p in range(1,v+1) for x in lc[p]))}; cells off: {off}; bowlers off: {sum(1 for p in range(1,v+1) if any(not lo<=x<=hi for x in lc[p]))}")
    print(f"  repeated trios: {sum(1 for t in trios.values() if t>1)}; distinct weeks (as group sets): {len(set(frozenset(frozenset(w[3*g:3*g+3]) for g in range(n)) for w in W))}/{r}")
    if round1:
        R=json.load(open(round1))['weeks']
        same=all(W[i][3*g:3*g+3]==R[i][3*g:3*g+3] for i in range(len(R)) for g in range(n))
        print(f"  first {len(R)} weeks identical to {round1.split('/')[-1]} (groups, lanes, order): {same}")
        for half,name in ((W[:len(R)],'round 1'),(W[len(R):],'round 2')):
            c=collections.Counter()
            for w in half:
                for g in range(n):
                    for a,b in itertools.combinations(sorted(w[3*g:3*g+3]),2): c[(a,b)]+=1
            print(f"  {name}: every couple exactly once: {len(c)==v*(v-1)//2 and set(c.values())=={1}}")
    return pairs_ok and off==0
if __name__=='__main__':
    ok=check(sys.argv[1], sys.argv[2] if len(sys.argv)>2 else None); print('  RESULT:', 'PASS' if ok else 'FAIL')
    d=json.load(open(sys.argv[1])); W=d['weeks']; v=d['players']; n=v//3
    if d['lambda']==2 and len(W)%2==0:
        h=len(W)//2
        for name,half in (('round 1',W[:h]),('round 2',W[h:])):
            c=collections.Counter(); lc=collections.Counter()
            for w in half:
                for g in range(n):
                    for a,b in itertools.combinations(sorted(w[3*g:3*g+3]),2): c[(a,b)]+=1
                    for p in w[3*g:3*g+3]: lc[(p,g)]+=1
            print(f"  {name}: every couple exactly once: {len(c)==v*(v-1)//2 and set(c.values())=={1}}; lane counts observed {sorted(set(lc[(p,g)] for p in range(1,v+1) for g in range(n)))}")
