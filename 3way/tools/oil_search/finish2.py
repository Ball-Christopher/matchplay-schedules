# input: json {"weeks":[[triples 0-based]], "blocks":[block id per week]} -> order blocks/weeks, lanes, positions, write outputs
import sys, json, random, itertools, math
from collections import Counter
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[3] / "tools"))
from positions import assign
src, v, outbase, method = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
d=json.load(open(src)); weeks=[[tuple(t) for t in w] for w in d["weeks"]]; bl=d["blocks"]
if len(sys.argv)>5: weeks=[[tuple(t) for t in w] for w in json.load(open(sys.argv[5]))]
n=v//3; r=v-1; assert len(weeks)==r
def pairs(w): return [frozenset(e) for t in w for e in itertools.combinations(t,2)]
B={}
for w,b in zip(weeks,bl): B.setdefault(b,[]).append(w)
for b,ws in B.items():
    c=Counter(e for w in ws for e in pairs(w)); assert max(c.values())==1, "clash in block"
# --- order: minimise number of prefixes with spread 2
allp=[frozenset(e) for e in itertools.combinations(range(v),2)]
def spreads(order):
    m=Counter(); out=[]
    for w in order:
        for e in pairs(w): m[e]+=1
        vals=[m[e] for e in allp]; out.append(max(vals)-min(vals))
    return out
best=None
for perm in itertools.permutations(B):
    b1,b2,b3=[B[x] for x in perm]
    zero=set(allp)-set(e for w in b1 for e in pairs(w))
    # choose smallest prefix set of b2 covering zero (must end up all covered by end of b2)
    for k in range(1,len(b2)+1):
        hit=None
        for sub in itertools.combinations(range(len(b2)),k):
            cov=set(e for i in sub for e in pairs(b2[i]))
            if zero<=cov: hit=sub; break
        if hit is not None: break
    # within the cover set, greedy order by most zero pairs covered first
    rest=[i for i in range(len(b2)) if i not in hit]; hit=list(hit); o2=[]; z=set(zero)
    while hit:
        i=max(hit,key=lambda i:len(z&set(pairs(b2[i])))); hit.remove(i); o2.append(b2[i]); z-=set(pairs(b2[i]))
    o2+= [b2[i] for i in rest]
    order=b1+o2+b3; sp=spreads(order)
    key=(max(sp[:-1]), sum(1 for x in sp if x>=2))
    if best is None or key<best[0]: best=(key,order,[len(b1),len(b2),len(b3)],sp)
key,order,blocks,sp=best
print("blocks",blocks,"worst spread",key[0],"weeks at spread 2:",key[1],sp)
# --- lanes: SA over per-week group permutation
lo,hi=r//n,-(-r//n)
def lanes(order,seed):
    rnd=random.Random(seed)
    W=[list(w) for w in order]
    for w in W: rnd.shuffle(w)
    cnt=[[0]*n for _ in range(v)]
    for w in W:
        for l,t in enumerate(w):
            for p in t: cnt[p][l]+=1
    pen=lambda c: (c-hi if c>hi else lo-c if c<lo else 0)
    cost=sum(pen(c) for row in cnt for c in row)
    T=0.6; it=0
    while cost and it<4000000:
        it+=1; T=max(0.08,T*0.999999)
        wi=rnd.randrange(r); a,b=rnd.sample(range(n),2); w=W[wi]
        dlt=0
        for p in w[a]: dlt+=pen(cnt[p][a]-1)+pen(cnt[p][b]+1)-pen(cnt[p][a])-pen(cnt[p][b])
        for p in w[b]: dlt+=pen(cnt[p][b]-1)+pen(cnt[p][a]+1)-pen(cnt[p][b])-pen(cnt[p][a])
        if dlt<=0 or rnd.random()<math.exp(-dlt/T):
            for p in w[a]: cnt[p][a]-=1; cnt[p][b]+=1
            for p in w[b]: cnt[p][b]-=1; cnt[p][a]+=1
            w[a],w[b]=w[b],w[a]; cost+=dlt
    return cost,W
W=[list(w) for w in order]
cnt=Counter((p,l) for w in W for l,t in enumerate(w) for p in t)
cost=sum(1 for p in range(v) for l in range(n) if not lo<=cnt[(p,l)]<=hi); print("lane violations",cost)
exact=(cost==0)
A=assign([[list(t) for t in w] for w in W],3)
flat=[[p+1 for g in w for p in g] for w in A]
# independent checks
off=0
for bs,be in zip(itertools.accumulate([0]+blocks[:-1]),itertools.accumulate(blocks)):
    c=Counter()
    for w in flat[bs:be]:
        assert sorted(w)==list(range(1,v+1))
        for g in range(n):
            for e in itertools.combinations(sorted(w[3*g:3*g+3]),2): c[e]+=1
    assert max(c.values())==1
tot=Counter(e for w in flat for g in range(n) for e in itertools.combinations(sorted(w[3*g:3*g+3]),2))
assert len(tot)==v*(v-1)//2 and set(tot.values())=={2}
print("checks ok; lane exact",exact)
out={"players":v,"group":3,"rounds":1,"lambda":2,"weeks":flat,"blocks":blocks,"lane_balance_exact":exact,"method":method}
json.dump(out,open(outbase+".json","w"),indent=1)
bs=list(itertools.accumulate([0]+blocks))
with open(outbase+".toml","w") as f:
    f.write(f"# {v} bowlers, groups of 3, {r} weeks, every couple meets exactly twice.\n")
    f.write(f"# Oil-pattern blocks (weeks, in order): {blocks} -- "+", ".join(f"block {i+1} = weeks {bs[i]+1}-{bs[i+1]}" for i in range(3))+".\n")
    f.write("# Within a block no couple shares a group twice, so each couple meets on 2 different patterns.\n")
    f.write(f"# Lane pairs = consecutive groups of 3 in each week; lane balance exact: {str(exact).lower()}. Worst prefix spread {key[0]}.\n")
    f.write(f"# Method: {method}\n[schedule]\nweeks = [\n")
    for w in flat: f.write("  "+json.dumps(w)+",\n")
    f.write("]\n")
