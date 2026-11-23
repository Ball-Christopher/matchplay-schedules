import itertools, sys
from common import *
tp = lambda t: list(itertools.combinations(t, 2))
T = [t for t in itertools.combinations(range(1, V + 1), 3) if not any(p in CP for p in tp(t))]
print("triangles in complement of C:", len(T), "of which round-1 trios:", sum(t in R1T for t in T))
print("transversal:", sum(len({SHORT[p] for p in t}) == 3 for t in T))
# enumerate parallel classes
def classes(T):
    out = []
    def rec(used, cur):
        if len(cur) == 6: out.append(tuple(cur)); return
        x = min(p for p in range(1, V + 1) if p not in used)
        for t in T:
            if t[0] == x and not (set(t) & used):
                rec(used | set(t), cur + [t])
    rec(frozenset(), []); return out
PC = classes(T); print("parallel classes:", len(PC))
ps = [set(e for t in c for e in tp(t)) for c in PC]
tr = [all(len({SHORT[p] for p in t}) == 3 for t in c) for c in PC]
nr = [sum(t in R1T for t in c) for c in PC]
n = 0; best = []
for i, j in itertools.combinations(range(len(PC)), 2):
    if not (ps[i] & ps[j]):
        n += 1; best.append((not (tr[i] or tr[j]), nr[i] + nr[j], i, j))
best.sort(); print("disjoint pairs of classes:", n, best[:10])
print("transversal classes", sum(tr))
cands = sorted((nr[i] + nr[j], i, j) for i, j in itertools.combinations(range(len(PC)), 2)
               if not (ps[i] & ps[j]) and (tr[i] or tr[j]))
print("X candidates with a transversal week:", len(cands), [c[0] for c in cands])
import json
json.dump([{"rep": c[0], "X": [PC[c[1]], PC[c[2]]] if tr[c[1]] else [PC[c[2]], PC[c[1]]]} for c in cands], open("out/xcands.json", "w"))
# triples of pairwise disjoint classes (k=3 option)
adj = {i: set() for i in range(len(PC))}
for i, j in itertools.combinations(range(len(PC)), 2):
    if not (ps[i] & ps[j]): adj[i].add(j); adj[j].add(i)
n3 = sum(len(adj[i] & adj[j] & set(range(j + 1, len(PC)))) for i in adj for j in adj[i] if j > i)
print("triples of disjoint classes:", n3)
