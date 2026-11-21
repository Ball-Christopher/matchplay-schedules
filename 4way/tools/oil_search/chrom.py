import sys, itertools, json, glob
def load(f):
    if f.endswith('.json'):
        d=json.load(open(f)); return d["weeks"] if isinstance(d,dict) else d
    return [list(map(int,l.split())) for l in open(f) if l.strip()]
def colour(W,k=4):
    r=len(W);cs=[{frozenset(c) for i in range(0,len(w),k) for c in itertools.combinations(w[i:i+k],2)} for w in W]
    adj=[[j for j in range(r) if j!=i and cs[i]&cs[j]] for i in range(r)]
    for b in range(1,r+1):
        col=[-1]*r;res=[None];nodes=[0]
        def bt(used):
            if res[0] or nodes[0]>300000:return
            nodes[0]+=1
            un=[i for i in range(r) if col[i]<0]
            if not un:res[0]=col[:];return
            u=max(un,key=lambda i:(len({col[j] for j in adj[i] if col[j]>=0}),len(adj[i])))
            forb={col[j] for j in adj[u] if col[j]>=0}
            for c in range(min(used+1,b)):
                if c not in forb:
                    col[u]=c;bt(max(used,c+1));col[u]=-1
                    if res[0]:return
        bt(0)
        if res[0]:return b,res[0]
if __name__=="__main__":
    for f in sys.argv[1:]:
        try:
            W=load(f)
            if len(W)!=23:continue
            b,c=colour(W);print(b,sorted([c.count(x) for x in range(b)],reverse=True),f.split('/')[-1],flush=True)
        except Exception as e:print("err",f,e)
