import json,itertools
from collections import Counter
d=json.load(open('../../../v18_oil.json'))
W=[[w[i:i+3] for i in range(0,18,3)] for w in d['weeks']]
def pairs(wk): return [tuple(sorted(x)) for g in wk for x in itertools.combinations(g,2)]
A=Counter(p for wk in W[:8] for p in pairs(wk))
allp=set(itertools.combinations(range(1,19),2))
F=allp-set(A); print("F",sorted(F))
m=Counter();sp=[]
for wk in W:
    m.update(pairs(wk)); sp.append(max(m[p] for p in allp)-min(m[p] for p in allp))
print("spread",sp)
for i in range(8,17): print(i+1,[p for p in pairs(W[i]) if p in F])
# 2-week subsets covering each F edge exactly once
for i,j in itertools.combinations(range(8,17),2):
    c=Counter(p for k in (i,j) for p in pairs(W[k]) if p in F)
    if len(c)==9 and max(c.values())==1: print("split",i+1,j+1)
pos=Counter()
for wk in W:
    for g in wk:
        for q,p in enumerate(g): pos[p,q]+=1
print({p:[pos[p,q] for q in range(3)] for p in range(1,19)})
lane=Counter((p,l) for wk in W for l,g in enumerate(wk) for p in g)
print({p:[lane[p,l] for l in range(6)] for p in range(1,19)})
