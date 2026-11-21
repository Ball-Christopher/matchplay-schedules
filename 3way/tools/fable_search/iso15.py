import sys,itertools,collections,json
def load(line):
    a=list(map(int,line.split()[2:])); return [[tuple(a[w*15+t*3:w*15+t*3+3]) for t in range(5)] for w in range(7)]
def prep(K):
    third={}; cls={}
    for w,W in enumerate(K):
        for T in W:
            a,b,c=T
            for x,y,z in ((a,b,c),(a,c,b),(b,c,a)): third[(x,y)]=z; third[(y,x)]=z
            cls[frozenset(T)]=w
    return third,cls
def isos(K1,K2,count_all=False):
    """number of isomorphisms K1->K2 preserving the resolution (stops at 1 unless count_all)"""
    t1,c1=prep(K1); t2,c2=prep(K2); n=0
    def extend(f,used,x,y):
        f=dict(f); used=set(used); f[x]=y; used.add(y); queue=[x]
        while queue:
            a=queue.pop()
            for b in list(f):
                if b==a: continue
                z=t1[(a,b)]; img=t2[(f[a],f[b])]
                if z in f:
                    if f[z]!=img: return None
                else:
                    if img in used: return None
                    f[z]=img; used.add(img); queue.append(z)
        return f,used
    def rec(f,used):
        nonlocal n
        if len(f)==15:
            m={}  # class map must be well defined
            for T,w in c1.items():
                w2=c2[frozenset(f[p] for p in T)]
                if m.setdefault(w,w2)!=w2: return
            n+=1; return
        x=min(p for p in range(15) if p not in f)
        for y in range(15):
            if y in used: continue
            r=extend(f,used,x,y)
            if r: rec(*r)
            if n and not count_all: return
    rec({},set()); return n
if __name__=='__main__':
    groups=collections.defaultdict(list)
    for l in open('k15_members.txt'): groups[l.split()[1]].append(load(l))
    reps=[]
    for k,Ks in groups.items():
        rs=[]
        for K in Ks:
            if not any(isos(K,R) for R in rs): rs.append(K)
        print('invariant',k,'members tested',len(Ks),'-> iso classes',len(rs),'|Aut| =',[isos(R,R,True) for R in rs])
        reps+=rs
    print('total pairwise non-isomorphic KTS(15):',len(reps), ' cross-check all pairs non-iso:', all(not isos(reps[i],reps[j]) for i in range(len(reps)) for j in range(i+1,len(reps))))
    auts=[isos(R,R,True) for R in reps]
    print('sum over classes of 15!*7/(1401400*9)/|Aut| =',sum(725760//a for a in auts),'(enumeration found 224640)')
    json.dump(reps,open('k15_reps.json','w'))
