import itertools, subprocess, sys
def colourable(S):
    adj=[[ (v+d)%23 for d in S]+[(v-d)%23 for d in S] for v in range(23)]
    col=[-1]*23
    def rec(v,mx):
        if v==23: return True
        for c in range(min(mx+1,3)+1):
            if all(col[u]!=c for u in adj[v]):
                col[v]=c
                if rec(v+1,max(mx,c)): return True
                col[v]=-1
        return False
    return rec(0,-1)
good=[]
for k in range(1,12):
    for S in itertools.combinations(range(1,12),k):
        if colourable(S): good.append(frozenset(S))
gs=set(good)
mx=[S for S in good if not any(S<T for T in gs)]
def canon(S):
    best=None
    for m in range(1,12):
        T=tuple(sorted(min(m*d%23,23-m*d%23) for d in S))
        if best is None or T<best: best=T
    return best
reps=sorted(set(canon(S) for S in mx))
print(len(good),len(mx),reps)
tot=0
for S in reps:
    mask=sum(1<<d for d in S)
    out=subprocess.run(['./dfsm',str(mask)],capture_output=True,text=True)
    n=len(out.stdout.splitlines()); tot+=n
    print(S,n,out.stderr.strip().splitlines()[-1] if out.stderr.strip() else 'no inf triple')
    if n: open('sol_%d.txt'%mask,'w').write(out.stdout)
print('total',tot)
