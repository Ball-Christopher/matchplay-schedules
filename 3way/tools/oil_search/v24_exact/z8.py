# Z_8 x 3 design: orbit weeks A (8), B (8), 7 invariant weeks I. Blocks X=A0-3+I_X, Y=A4-7+I_Y, Z=B+I_Z.
import sys, random, json, itertools
seed=int(sys.argv[1]); z=int(sys.argv[2]); random.seed(seed)
def orb(p,q):
    c,i=divmod(p,8); d,j=divmod(q,8)
    if c>d: c,d,i,j=d,c,j,i
    if c==d:
        e=(j-i)%8
        if e==4: return (c,c,4),0
        if e>4: return (c,c,8-e),j
        return (c,c,e),i
    return (c,d,(j-i)%8),i
T=[]
for t in itertools.combinations(range(24),3):
    T.append((t,[orb(t[0],t[1]),orb(t[0],t[2]),orb(t[1],t[2])]))
by=[[] for _ in range(24)]
for t in T: by[t[0][0]].append(t)
class TO(Exception): pass
def solve(cap, need_min, offset4, limit):
    used=[False]*24; cnt={}; pos={}; res=[]; nodes=[0]
    def rec():
        nodes[0]+=1
        if nodes[0]>limit: raise TO
        try: x=next(i for i in range(24) if not used[i])
        except StopIteration:
            return all(cnt.get(o,0)>=m for o,m in need_min.items())
        cand=[t for t in by[x] if not used[t[0][1]] and not used[t[0][2]]]
        random.shuffle(cand)
        for t,os in cand:
            ok=True; done=[]
            for o,p in os:
                c=cnt.get(o,0)
                if c>=cap.get(o,0): ok=False;break
                if c==1 and o[2]!=4 and (not offset4 or (pos[o]-p)%8!=4): ok=False;break
                if c==1 and o[2]==4: ok=False;break
                cnt[o]=c+1
                if c==0: pos[o]=p
                done.append(o)
            if ok:
                for y in t: used[y]=True
                res.append(t)
                if rec(): return True
                res.pop()
                for y in t: used[y]=False
            for o in done: cnt[o]-=1
        return False
    if rec(): return res,dict(cnt)
    return None
allorb=set(o for t in T for o,_ in t[1])
while True:
    # invariant weeks
    while True:
        a=random.sample(range(8),7); b=random.sample(range(8),7)
        if len(set((y-x)%8 for x,y in zip(a,b)))==7: break
    I=list(zip(a,b)); IZ=set(random.sample(range(7),z))
    capA={}; minA={}
    Iorb={}
    for t,(x,y) in enumerate(I):
        for o in ((0,1,x),(0,2,y),(1,2,(y-x)%8)): Iorb[o]=t
    for o in allorb:
        if o[0]==o[1]:
            if o[2]==4: capA[o]=1; minA[o]=1
            else: capA[o]=2; minA[o]=1
        elif o in Iorb:
            if Iorb[o] in IZ: capA[o]=1; minA[o]=1
            else: capA[o]=0
        else: capA[o]=2; minA[o]=1
    try: r=solve(capA,minA,True,200000)
    except TO: print("A timeout",flush=True); continue
    if not r: print("A none",flush=True); continue
    A,cntA=r
    capB={}
    for o in allorb:
        tot=2-cntA.get(o,0)-(1 if o in Iorb else 0)
        if o[2]==4 and o[0]==o[1]: tot=0
        capB[o]=tot
    assert sum(capB.values())==24 and all(0<=v<=1 for v in capB.values()),capB
    for tries in range(20):
        try: r=solve(capB,{},False,200000)
        except TO: r=None
        if r: break
    if not r: print("B fail",flush=True); continue
    json.dump({"A":A,"B":r[0],"I":I,"IZ":sorted(IZ)},open(f"z8_{seed}_{z}.json","w"))
    print("FOUND",flush=True); break
