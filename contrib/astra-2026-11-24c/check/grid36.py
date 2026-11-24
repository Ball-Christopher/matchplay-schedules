"""36 in fours, main round first: can the 8-week class of 4way/v36_oil follow the main round's
last clash-free block (3 weeks) under some relabelling?
Checks from the weeks: (1) the couples the 8-week class never uses form 4 disjoint K9s plus
9 disjoint K4s ('layers' and 'columns', each column one bowler per layer); (2) so a tail quartet
mapped into them is a whole layer-quartet or a whole column; (3) brute force: two weeks that
each use exactly one column can't be couple-disjoint inside a layer; with columns disjoint
across the 3 clash-free tail weeks, x columns per week with 9-x divisible by 4 gives x in
{1,5,9}, and every admissible pattern ((1,1,1), (5,1,1) in some order) has two x=1 weeks.
So NO relabelling exists, whatever the tail looks like."""
import json
from itertools import combinations
import os
R=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../../..'))
def grp(w,k): return [w[i:i+k] for i in range(0,len(w),k)]
oil=json.load(open(f'{R}/4way/v36_oil.json'))['weeks']
blocks=[];cur=[];used=set()
for w in oil:
    ps={frozenset(p) for g in grp(w,4) for p in combinations(g,2)}
    if used&ps: blocks.append(cur);cur=[];used=set()
    cur.append(w);used|=ps
blocks.append(cur)
cls=[b for b in blocks if len(b)==8][0]
used={frozenset(p) for w in cls for g in grp(w,4) for p in combinations(g,2)}
free={frozenset(p) for p in combinations(range(1,37),2)}-used
adj={a:{b for b in range(1,37) if frozenset((a,b)) in free} for a in range(1,37)}
# maximal cliques of size 9 = layers
layers=[]; seen=set()
for a in range(1,37):
    if a in seen: continue
    # layer of a: a plus its neighbours that are adjacent to >=7 of a's other neighbours
    L={a}|{b for b in adj[a] if len(adj[a]&adj[b])>=7}
    layers.append(sorted(L)); seen|=L
assert len(layers)==4 and all(len(L)==9 for L in layers), layers
lay={p:i for i,L in enumerate(layers) for p in L}
for L in layers: assert all(frozenset(p) in free for p in combinations(L,2))
cross=[p for p in free if lay[min(p)]!=lay[max(p)]]
# cross free edges form 9 disjoint K4 (columns), one bowler per layer
col_adj={a:{b for b in adj[a] if lay[b]!=lay[a]} for a in range(1,37)}
cols={frozenset({a}|col_adj[a]) for a in range(1,37)}
assert len(cols)==9 and all(len(c)==4 and len({lay[p] for p in c})==4 for c in cols)
assert all(len(col_adj[a])==3 for a in range(1,37))
print('free graph = 4 K9 (layers) + 9 K4 (columns):', len(free)==4*36+9*6)
# K4s in free graph
k4=[q for L in layers for q in combinations(L,4)]+[tuple(sorted(c)) for c in cols]
cl=0
for a in range(1,37):
    for b,c,d in combinations(sorted(x for x in adj[a] if x>a),3):
        if frozenset((b,c)) in free and frozenset((b,d)) in free and frozenset((c,d)) in free: cl+=1
print('4-cliques in free graph:',cl,'= 4*126 layer quartets + 9 columns:',cl==4*126+9)
# check claim (2) on the abstract structure by brute force over mixed quartets is immediate:
# two bowlers of one layer are never both adjacent to the same bowler of another layer (one per column).
# (3) two weeks each with one column: inside a 9-point layer, partitions of 9-{c1} and 9-{c2}
pts=range(9); bad=0; ok=0
for c1,c2 in [(0,1)]:
    S1=[p for p in pts if p!=c1]; S2=[p for p in pts if p!=c2]
    for A in combinations(S1,4):
        if 0 not in A and S1[0] not in A: continue
        B=tuple(p for p in S1 if p not in A)
        for C in combinations(S2,4):
            D=tuple(p for p in S2 if p not in C)
            if all(len(set(X)&set(Y))<=1 for X in (A,B) for Y in (C,D)): ok+=1
print('couple-disjoint layer splits for two one-column weeks:', ok)
pats=sorted({tuple(sorted(t)) for t in __import__('itertools').product((1,5,9),repeat=3) if sum(t)<=9})
print('admissible column patterns over 3 weeks:', pats, '-> each has two one-column weeks:', all(t.count(1)>=2 for t in pats))
