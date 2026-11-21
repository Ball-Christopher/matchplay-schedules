# 1-rotational search: base week on Z_p + inf; weeks B+i. Week i and i+c clash for c in conflict set.
# Require conflict set within "middle third" differences (times a multiplier) -> 3 arcs colouring.
import sys, random, json
p=int(sys.argv[1]); seed=int(sys.argv[2]); random.seed(seed)
h=(p-1)//2; INF=p
a=(p+2)//3          # largest arc length: 6 for 17, 8 for 23
A=set(c for c in range(1,p) if a<=c<=p-a)   # allowed conflict differences
occ={d:[] for d in range(1,h+1)}
used=[False]*(p+1); triples=[]
sys.setrecursionlimit(10000)
def addpair(x,y,log):
    d=(y-x)%p
    if d>h: x,y=y,x; d=p-d
    o=occ[d]
    if len(o)>=2: return False
    if o and (o[0]-x)%p not in A: return False
    o.append(x); log.append(d); return True
nodes=0
def rec():
    global nodes
    nodes+=1
    if nodes>400000: raise TimeoutError
    try: x=next(i for i in range(p+1) if not used[i])
    except StopIteration: return True
    used[x]=True
    rest=[i for i in range(x+1,p+1) if not used[i]]
    random.shuffle(rest)
    for i,y in enumerate(rest):
        for z in rest[i+1:]:
            y2,z2=min(y,z),max(y,z)
            log=[]
            ok=True
            if z2==INF:
                # triple {inf,x,y2}: pair diff plus conflict x-y2
                ok=((x-y2)%p in A) and addpair(x,y2,log)
            else:
                ok=addpair(x,y2,log) and addpair(x,z2,log) and addpair(y2,z2,log)
            if ok:
                used[y2]=used[z2]=True; triples.append((x,y2,z2))
                if rec(): return True
                triples.pop(); used[y2]=used[z2]=False
            for d in log: occ[d].pop()
    used[x]=False
    return False
while True:
    try:
        nodes=0
        for d in occ: occ[d]=[]
        used=[False]*(p+1); triples=[]
        if rec(): break
        print("exhausted"); sys.exit()
    except TimeoutError: pass
print(json.dumps(triples))
