import json, itertools, random, math, sys
from collections import Counter
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[3] / "tools"))
from positions import assign
OUT=str(__import__("pathlib").Path(__file__).resolve().parents[2])
def reps(W,blocks):
    tot=0;i=0
    for b in blocks:
        c=Counter(frozenset(p) for wk in W[i:i+b] for g in wk for p in itertools.combinations(g,2)); tot+=sum(n-1 for n in c.values()); i+=b
    return tot
def spreads(W,v):
    m=Counter();out=[];cp=list(itertools.combinations(range(1,v+1),2))
    for wk in W:
        for g in wk:
            for a,b in itertools.combinations(sorted(g),2): m[(a,b)]+=1
        vals=[m[c] for c in cp]; out.append(max(vals)-min(vals))
    return out,m
def lane_off(W,v):
    n=len(W[0]);r=len(W);lo,hi=r//n,-(-r//n);c=Counter()
    for wk in W:
        for l,g in enumerate(wk):
            for p in g:c[(p,l)]+=1
    exc=sum(max(0,c[(p,l)]-hi)+max(0,lo-c[(p,l)]) for p in range(1,v+1) for l in range(n))
    off=sum(1 for p in range(1,v+1) if any(not lo<=c[(p,l)]<=hi for l in range(n)))
    return exc,off
def lane_sa(W,v,rng,steps=200000):
    W=[list(wk) for wk in W];cur=lane_off(W,v)[0];best=(cur,[list(w) for w in W]);T=1.0
    for it in range(steps):
        if cur==0:break
        w=rng.randrange(len(W));i,j=rng.sample(range(len(W[w])),2);W[w][i],W[w][j]=W[w][j],W[w][i]
        n=lane_off(W,v)[0]
        if n<=cur or rng.random()<math.exp((cur-n)/T):
            cur=n
            if cur<best[0]:best=(cur,[list(x) for x in W])
        else:W[w][i],W[w][j]=W[w][j],W[w][i]
        T=max(0.05,T*0.99997)
    return best[1]
def order(blks,v,rng,steps=20000):
    # blks: list of lists of weeks. permute blocks and weeks inside blocks; minimise (max prefix spread excluding last, sum sq)
    def flat(b):return [w for x in b for w in x]
    def cost(b):
        s=spreads(flat(b),v)[0];return max(s[:-1])*1000+sum(x*x for x in s)
    cur=cost(blks);best=(cur,[list(b) for b in blks]);T=30
    for it in range(steps):
        nb=[list(b) for b in blks]
        if rng.random()<0.3:i,j=rng.sample(range(len(nb)),2);nb[i],nb[j]=nb[j],nb[i]
        else:
            b=rng.choice([x for x in nb if len(x)>1]);i,j=rng.sample(range(len(b)),2);b[i],b[j]=b[j],b[i]
        n=cost(nb)
        if n<=cur or rng.random()<math.exp((cur-n)/T):
            blks=nb;cur=n
            if cur<best[0]:best=(cur,[list(b) for b in blks])
        T=max(0.5,T*0.9995)
    return best[1]
def finish(name,v,blks,method,rng,steps=20000,fixlanes=False):
    if fixlanes:
        sizes=[len(b) for b in blks];W=lane_sa([w for b in blks for w in b],v,rng);blks=[];i=0
        for s in sizes:blks.append(W[i:i+s]);i+=s
    blks=order(blks,v,rng,steps)
    W=[w for b in blks for w in b];blocks=[len(b) for b in blks]
    W=assign(W,4)
    assert all(sorted(p for g in wk for p in g)==list(range(1,v+1)) for wk in W)
    sp,m=spreads(W,v);assert set(m.values())=={3} and len(m)==v*(v-1)//2
    rp=reps(W,blocks);exc,off=lane_off(W,v)
    flat=[[p for g in wk for p in g] for wk in W]
    d={"players":v,"group":4,"rounds":1,"lambda":3,"weeks":flat,"blocks":blocks,"block_repeats":rp,"lane_balance_exact":off==0,"method":method}
    json.dump(d,open(f"{OUT}/{name}.json","w"),indent=1)
    hdr=f"# {v} players, 4 per lane pair, {v-1} weeks: every couple meets exactly 3 times.\n# Oil-pattern blocks (consecutive weeks): {' + '.join(map(str,blocks))} = {v-1} weeks.\n"
    i=1
    for k,b in enumerate(blocks):hdr+=f"#   block {k+1}: weeks {i}-{i+b-1}\n";i+=b
    hdr+=f"# Same-block repeat meetings: {rp}" + (" (no couple meets twice on one pattern; every couple meets on 3 different patterns)" if rp==0 else "")+".\n"
    hdr+=f"# Lane pairs: {'exact (floor/ceil for every bowler)' if off==0 else str(off)+' bowler(s) one off'}. Groups in lane-pair order; within a group: left lane 1st, right lane 1st, left lane 2nd, right lane 2nd.\n"
    open(f"{OUT}/{name}.toml","w").write(hdr+"[schedule]\nweeks = [\n"+"".join("  "+json.dumps(w)+",\n" for w in flat)+"]\n")
    print(name,"blocks",blocks,"repeats",rp,"lane off",off,"prefix",sp,"worst",max(sp[:-1]))
if __name__=="__main__":
    rng=random.Random(1)
    if sys.argv[1]=="20":
        rows=[list(map(int,l.split())) for l in open("z20_4.txt")]
        W=[[[p+1 for p in r[i:i+4]] for i in range(0,20,4)] for r in rows]
        blks=[W[0:5],W[5:10],W[10:15],W[15:19]]
        finish("v20_oil",20,blks,"Z_5 x 4 classes: 3 base weeks developed mod 5 (each orbit a clash-free 5-week block) + 4 Z_5-invariant weeks (4-week block); found by annealing on difference types with a within-block penalty; Z_5 also rotates the lane pairs (exhaustive lane search); block/week order annealed for prefix spread; positions by de Werra (positions.assign).",rng)
