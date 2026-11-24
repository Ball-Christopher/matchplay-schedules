"""Can the weeks of a lambda=3 fours file be reordered so every prefix has spread <= 2?
Direct z3 model over week positions (no pivot reduction): pos[w] in 0..r-1 distinct;
for every prefix length L, not (some couple fully inside AND some couple fully outside)."""
import json,sys,os
from itertools import combinations
from z3 import Int,Solver,Distinct,And,Or,Not,Bool,If,sat,Implies
R=os.environ.get('REPO',os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../../..')))
for name in sys.argv[1:]:
    d=json.load(open(f'{R}/4way/{name}.json')); W=d['weeks']; k=4; r=len(W); v=d['players']
    meets={}
    for wi,w in enumerate(W):
        for i in range(0,v,k):
            for p in combinations(sorted(w[i:i+k]),2): meets.setdefault(p,[]).append(wi)
    triples={tuple(t) for t in meets.values()}
    assert all(len(t)==3 for t in triples)
    pos=[Int(f'p{w}') for w in range(r)]
    s=Solver(); s.add([And(0<=x,x<r) for x in pos]); s.add(Distinct(pos))
    # last[t] = max pos of triple, first[t] = min pos.  Spread 3 at prefix L iff exists t with last<L and t' with first>=L.
    # Need: for all t,t': not(last(t) < first(t'))  ... i.e. for every pair of triples, last(t) >= first(t')
    # (if last(t) < first(t'), the prefix L=last(t)+1 has t inside and t' outside).
    def mx(t): return [pos[w] for w in t]
    T=sorted(triples)
    for a in T:
        for b in T:
            if a==b: continue
            # last(a) >= first(b): some week of a is >= some... need max(a) >= min(b)
            s.add(Or([pos[x] >= pos[y] for x in a for y in b]))
    res=s.check()
    print(name, r,'weeks', len(T),'distinct couple triples ->', 'spread<=2 order EXISTS' if res==sat else str(res))
