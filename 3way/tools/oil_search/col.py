import sys, itertools
p=int(sys.argv[1]); h=(p-1)//2
def col3(C):
    C=[c for d in C for c in (d,p-d)]
    col=[-1]*p
    def rec(i,mx):
        if i==p: return True
        for c in range(min(mx+1,2)+1):
            if all(col[(i-d)%p]!=c for d in C):
                col[i]=c
                if rec(i+1,max(mx,c)): return True
                col[i]=-1
        return False
    return list(col) if rec(0,-1) else None
good=[]
for k in range(h,0,-1):
    for C in itertools.combinations(range(1,h+1),k):
        if any(set(C)<=set(g) for g in good): continue
        if col3(C): good.append(C)
# reduce by multipliers
seen=set(); out=[]
for g in good:
    key=min(tuple(sorted(min(m*d%p,p-m*d%p) for d in g)) for m in range(1,h+1))
    if key not in seen: seen.add(key); out.append(g)
for g in out: print(g, col3(g))
