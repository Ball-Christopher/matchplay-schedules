"""Check the 36-in-trios checkpoint: three 12-bowler layers, and the 3-week bridge onto the oil round's tail."""
import json,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from checkm import repo_first,greedy
from itertools import combinations
L=json.load(open(sys.argv[1]))
pts=[sorted({x for w in lay for g in w for x in g}) for lay in L]
print('layers partition 1..36:',sorted(sum(pts,[]))==list(range(1,37)))
for lay,p in zip(L,pts):
    c={}
    for w in lay:
        assert sorted(x for g in w for x in g)==p
        for g in w:
            for q in combinations(sorted(g),2): c[q]=c.get(q,0)+1
    print('layer: couples',len(c),'meet',set(c.values()),'blocks',greedy([sum(w,[]) for w in lay],3))
W=repo_first(36,3,'oil'); g=greedy(W,3)
bridge=[sum(sum((L[i][w] for i in range(3)),[]),[]) for w in range(3)]
print('repo oil blocks',g,'; tail + 3 bridge weeks clash-free run:',greedy(W[-g[-1]:]+bridge,3))
