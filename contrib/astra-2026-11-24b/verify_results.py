"""From the unpacked archive run python verify_results.py [path-to-checkout-at-33d41db]."""
from collections import Counter
from itertools import combinations
from pathlib import Path
import hashlib, json, sys
root=Path(__file__).resolve().parent
def exact(counter, people, size, rounds):
    for x in people:
        v=[counter[x,j] for j in range(size)]
        assert sum(v)==rounds and max(v)-min(v)<=1
def check(weeks,k,multiplicity):
    v=len(weeks[0]);people=range(1,v+1);universe=list(combinations(people,2))
    meetings=Counter();lanes=Counter();positions=Counter();prefix=[];cuts=[];seen=set()
    for row in weeks:
        assert sorted(row)==list(people)
        pairs={p for i in range(0,v,k) for p in combinations(sorted(row[i:i+k]),2)}
        if not cuts or seen & pairs:cuts.append(0);seen.clear()
        cuts[-1]+=1;seen.update(pairs);meetings.update(pairs)
        for i,x in enumerate(row):lanes[x,i//k]+=1;positions[x,i%k]+=1
        values=[meetings[p] for p in universe];prefix.append(max(values)-min(values))
    assert len(meetings)==len(universe) and set(meetings.values())=={multiplicity}
    exact(lanes,people,v//k,len(weeks));exact(positions,people,k,len(weeks))
    return cuts,max(prefix)
for f in sorted([*root.glob('*.json'),*root.glob('two_rounds/*.json')]):
    d=json.loads(f.read_text());W=d['weeks'];k=d['group'];rr=d['rounds'];lam=d['lambda'];v=d['players']
    assert len(W)*(k-1)==lam*rr*(v-1)
    cuts,spread=check(W,k,lam*rr)
    if 'blocks' in d:assert cuts==d['blocks']
    if rr==2:
        half=len(W)//2
        for a in [W[:half],W[half:]]:check(a,k,lam)
        rel=f"{k}way/v{v}{'_oil' if d['first_round']=='oil' else ''}.json"
        digest=hashlib.sha256(json.dumps(W[:half],separators=(',',':')).encode()).hexdigest()
        assert digest==d['first_round_week_sha256']
        if len(sys.argv)>1:assert W[:half]==json.loads((Path(sys.argv[1])/rel).read_text())['weeks']
    if f.name.startswith('index1'):assert spread==1
    if f.name=='fours36_oil.json':
        assert spread==2 and cuts==[9,9,9,8]
        for t in range(1,36):
            c=Counter((x,i%4) for w in W[:t] for i,x in enumerate(w))
            exact(c,range(1,37),4,t)
    print(f.name,'OK')
for f in sorted(root.glob('qualifying/*.json')):
    d=json.loads(f.read_text());m,k,b=d['M'],d['K'],d['B'];P=range(1,m*k+1);c=Counter();e=Counter();follows=Counter()
    for w in d['draw']:
        assert len(w)==m and sorted(sum(w,[]))==list(P)
        for lane,g in enumerate(w):
            assert len(g)==k
            c.update((x,lane) for x in g);e.update(combinations(sorted(g),2))
            cyc=g[::2]+g[1::2];follows.update(zip(cyc,cyc[1:]+cyc[:1]))
    exact(c,P,m,b);assert max(e.values())==d['score']['max_meet'] and max(follows.values())==d['score']['max_follow']
    print(f.name,'OK')
