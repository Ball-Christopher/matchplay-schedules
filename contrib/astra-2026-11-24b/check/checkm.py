import json,sys,os
from itertools import combinations
import os
REPO=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../..'))
def groups(w,k): return [w[i:i+k] for i in range(0,len(w),k)]
def greedy(weeks,k):
    out=[];used=set();n=0
    for w in weeks:
        ps={frozenset(p) for g in groups(w,k) for p in combinations(g,2)}
        if used & ps: out.append(n);used=set();n=0
        used|=ps;n+=1
    out.append(n);return out
def stats(weeks,v,k):
    n=v//k; R=len(weeks)
    meet={};lane=[[0]*n for _ in range(v+1)];pos=[[0]*k for _ in range(v+1)]
    for w in weeks:
        assert sorted(w)==list(range(1,v+1)),'not a partition'
        for li,g in enumerate(groups(w,k)):
            for i,x in enumerate(g): lane[x][li]+=1;pos[x][i]+=1
            for p in combinations(sorted(g),2): meet[p]=meet.get(p,0)+1
    lam=set(meet.get(p,0) for p in combinations(range(1,v+1),2))
    lo,hi=R//n,-(-R//n); lane_off=sum(1 for x in range(1,v+1) if min(lane[x])<lo or max(lane[x])>hi)
    plo,phi=R//k,-(-R//k); pos_off=sum(1 for x in range(1,v+1) if min(pos[x])<plo or max(pos[x])>phi)
    # prefix spread
    cnt={};worst=0
    for w in weeks:
        for g in groups(w,k):
            for p in combinations(sorted(g),2): cnt[p]=cnt.get(p,0)+1
        vals=[cnt.get(p,0) for p in combinations(range(1,v+1),2)]
        worst=max(worst,max(vals)-min(vals))
    return dict(R=R,lam=sorted(lam),lane_off=lane_off,pos_off=pos_off,spread=worst,distinct=len({tuple(sorted(tuple(sorted(g)) for g in groups(w,k))) for w in weeks}))
def repo_first(v,k,which):
    d='3way' if k==3 else '4way'
    return json.load(open(f"{REPO}/{d}/v{v}{'_oil' if which=='oil' else ''}.json"))['weeks']
if __name__=='__main__':
    for f in sys.argv[1:]:
        a=json.load(open(f)); v,k=a['players'],a['group']; W=a['weeks']
        line=os.path.basename(f)+f": v{v} k{k}"
        if a.get('rounds')==2:
            R=len(W)//2; first=repo_first(v,k,a['first_round'])
            same=(first==W[:R])
            s1,s2,sa=stats(W[:R],v,k),stats(W[R:],v,k),stats(W,v,k)
            g=greedy(W,k)
            line+=f" first==repo:{same} r1 {s1['lam']} lo{s1['lane_off']} po{s1['pos_off']} | r2 {s2['lam']} lo{s2['lane_off']} po{s2['pos_off']} | all {sa['lam']} lo{sa['lane_off']} po{sa['pos_off']} | greedy {len(g)} {g} claim {len(a.get('blocks',[]))} {a.get('blocks')==g}"
            line+=f" | repo r1 greedy {len(greedy(first,k))}"
        else:
            s=stats(W,v,k); g=greedy(W,k)
            line+=f" {s} greedy {g} claim {a.get('blocks')}"
        print(line)
