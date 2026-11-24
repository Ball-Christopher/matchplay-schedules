import json,sys
from itertools import combinations,product
R=json.load(open(sys.argv[1]))
def comps(tris):
    # components of intersection graph of triples
    tris=[set(t) for t in tris]; seen=set(); out=[]
    for i in range(len(tris)):
        if i in seen: continue
        st=[i]; seen.add(i); n=0
        while st:
            a=st.pop(); n+=1
            for j in range(len(tris)):
                if j not in seen and tris[a]&tris[j]: seen.add(j); st.append(j)
        out.append(n)
    return tuple(sorted(out))
invs=[]
for idx,res in enumerate(R):
    assert len(res)==7 and all(len(c)==5 for c in res)
    for c in res: assert sorted(x for t in c for x in t)==list(range(15))
    pairs={}
    for c in res:
        for t in c:
            for p in combinations(sorted(t),2): pairs[p]=pairs.get(p,0)+1
    assert len(pairs)==105 and set(pairs.values())=={1}
    T=[frozenset(t) for c in res for t in c]; Ts=set(T)
    # Pasch count: 4 triples on 6 points, each point in 2
    third={}
    for t in T:
        for a,b in combinations(sorted(t),2): third[(a,b)]=third[(b,a)]=next(iter(t-{a,b}))
    pasch=0
    for t1,t2 in combinations(T,2):
        if len(t1&t2)==1:
            (x,)=t1&t2; a,b=sorted(t1-{x}); c,d=sorted(t2-{x})
            # completes to pasch if third(a,c)==third(b,d) (or a,d / b,c)
            for (p,q),(r,s) in [((a,c),(b,d)),((a,d),(b,c))]:
                if third[(p,q)]==third[(r,s)] and third[(p,q)] not in t1|t2: pasch+=1
    pasch//=6
    pairinv=tuple(sorted(comps(res[i]+res[j]) for i,j in combinations(range(7),2)))
    triinv=tuple(sorted(comps(res[i]+res[j]+res[k]) for i,j,k in combinations(range(7),3)))
    # count of triples meeting all classes pattern: for each point-pair-of-classes cycle lengths
    def cyc(i,j):
        # 2-regular-ish: graph on points where edges from triples of classes i,j; per point degree 4; use component sizes of point graph after removing? use number of triangles from class pairs forming "transversal"
        cnt=0
        for t in res[i]:
            for u in res[j]:
                cnt+= len(set(t)&set(u))==1
        return cnt
    invs.append((pasch,pairinv,triinv))
    print(idx,'valid KTS(15)','pasch',pasch,'pair-union comps',sorted(set(pairinv)),'distinct-triple-inv',len(set(triinv)))
print('pairwise distinct invariants:',len(set(invs))==7)
# lane enumeration
tot=0
for idx,res in enumerate(R):
    lanes=[]
    for choice in product(range(5),repeat=7):
        cnt=[0]*15
        for w,c in enumerate(choice):
            for x in res[w][c]: cnt[x]+=1
        if min(cnt)>=1 and max(cnt)<=2: lanes.append(choice)
    # exact cover: 5 lanes, each week's 5 groups each used once
    sols=0
    def rec(used,k,start):
        global sols
        if k==5: sols+=1; return
        for li in range(start,len(lanes)):
            L=lanes[li]
            if all(L[w] not in used[w] for w in range(7)):
                for w in range(7): used[w].add(L[w])
                rec(used,k+1,li+1)
                for w in range(7): used[w].discard(L[w])
            if sols: return
    rec([set() for _ in range(7)],0,0)
    print(idx,'candidate lanes',len(lanes),'lane partitions found',sols)
    tot+=sols
print('TOTAL lane-balanced allocations:',tot)
