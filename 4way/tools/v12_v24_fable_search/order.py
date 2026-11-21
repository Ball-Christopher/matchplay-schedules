import sys,itertools,random,math,numpy as np,glob,json
best=None
for f in sorted(glob.glob(sys.argv[1])):
    W=[list(map(int,l.split())) for l in open(f) if l.strip()]
    v=len(W[0]);r=len(W);idx={p:i for i,p in enumerate(itertools.combinations(range(1,v+1),2))}
    X=np.zeros((r,len(idx)),dtype=np.int16)
    for w,wk in enumerate(W):
        for L in range(v//4):
            for a,b in itertools.combinations(sorted(wk[4*L:4*L+4]),2): X[w,idx[a,b]]+=1
    def cost(o):
        c=np.cumsum(X[o],axis=0);s=c.max(1)-c.min(1);return int(s.max())*1000+int(s.sum())
    random.seed(1)
    for rs in range(int(sys.argv[2])):
        o=list(range(r));random.shuffle(o);c=cost(o);T=3.0
        for it in range(int(sys.argv[3])):
            T=3.0*(0.02)**(it/int(sys.argv[3]))
            i,j=random.sample(range(r),2);o[i],o[j]=o[j],o[i];nc=cost(o)
            if nc<=c or random.random()<math.exp(-(nc-c)/T): c=nc
            else: o[i],o[j]=o[j],o[i]
        if best is None or c<best[0]: best=(c,f,[W[k] for k in o]);print(c,f,flush=True)
json.dump({"cost":best[0],"src":best[1],"weeks":best[2]},open(sys.argv[4],"w"))
