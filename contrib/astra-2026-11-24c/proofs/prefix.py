from itertools import combinations
from collections import defaultdict,Counter
from pathlib import Path
import json
def bicolour(edges,R,B):
 while True:
  open_edges=[];rr=bb=0
  for e in edges:
   r=e&R;b=e&B
   if r and b:continue
   empty=e&~(R|B)
   if not empty:return None
   if empty.bit_count()==1:
    if r:bb|=empty
    if b:rr|=empty
   open_edges.append(e)
  if rr&bb:return None
  if not rr and not bb:break
  R|=rr;B|=bb;edges=open_edges
 if not open_edges:return R
 tally=Counter()
 for e in open_edges:
  empty=e&~(R|B);weight=4 if empty.bit_count()==2 else 1
  while empty:
   x=empty&-empty;tally[x]+=weight;empty-=x
 x=max(tally,key=tally.get)
 res=bicolour(open_edges,R|x,B)
 return bicolour(open_edges,R,B|x) if res is None else res
def scan(W):
 E=defaultdict(int)
 for i,w in enumerate(W):
  for j in range(0,len(w),4):
   for p in combinations(sorted(w[j:j+4]),2):E[p]|=1<<i
 assert all(e.bit_count()==3 for e in E.values())
 for k in range(len(W)):
  edges=list({e for e in E.values() if not (e>>k)&1})
  R=bicolour(edges,1 if k else 2,0)
  if R is not None:return [i for i in range(len(W)) if R>>i&1]+[k]+[i for i in range(len(W)) if i!=k and not R>>i&1]
if __name__ == '__main__':
 root=Path(__file__).resolve().parents[1]
 for n in (20,24,36):
  weeks=json.loads((root/'inputs'/f'main{n}.json').read_text())['weeks']
  assert scan(weeks) is None
  print(f'{n} in fours: no spread-two order for these exact weeks')
