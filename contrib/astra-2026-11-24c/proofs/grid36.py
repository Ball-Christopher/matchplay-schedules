import json,itertools,collections
from pathlib import Path
from itertools import combinations,product
W=json.load(open(Path(__file__).resolve().parents[1]/'inputs/main36.json'))['weeks'][32:35]
G=[[tuple(w[i:i+4]) for i in range(0,36,4)] for w in W]
pop=list(range(1,37))
counts=collections.Counter()
for sizes in [(1,1,1),(5,1,1),(1,5,1),(1,1,5)]:
 for D in product(*(combinations(range(9),s) for s in sizes)):
  cols=[g for w,gg in enumerate(G) for j,g in enumerate(gg) if j in D[w]]
  if len(set(sum(cols,())))!=4*len(cols):continue
  counts['disjoint']+=1
  parent=list(range(37))
  def find(x):
   while x!=parent[x]:x=parent[x]
   return x
  for w,gg in enumerate(G):
   for j,g in enumerate(gg):
    if j not in D[w]:
     for x in g[1:]:parent[find(x)]=find(g[0])
  comp=collections.defaultdict(list)
  for x in pop:comp[find(x)].append(x)
  if max(map(len,comp.values()))>9:continue
  if any(len(set(map(find,c)))!=4 for c in cols):continue
  counts['components_fit']+=1
  components=sorted(comp.values(),key=len,reverse=True)
  bins=[[] for _ in range(4)]
  def fit(k):
   if k==len(components):return True
   g=components[k]
   for v in bins:
    if len(v)+len(g)<=9 and all(len(set(v+g)&set(c))<=1 for c in cols):
     v.extend(g)
     if fit(k+1):return True
     del v[-len(g):]
    if not v:break
  if fit(0):print(bins,cols);raise SystemExit
assert counts == {"disjoint":108}
print(counts)
