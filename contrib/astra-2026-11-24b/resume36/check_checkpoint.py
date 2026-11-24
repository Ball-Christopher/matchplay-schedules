"""Check the three-layer bridge independently of any proposed lane allocation."""
from itertools import combinations
from collections import Counter
from pathlib import Path
import json
root=Path(__file__).resolve().parent
def load(f):return json.loads((root/f).read_text())
def edges(groups):return [p for g in groups for p in combinations(sorted(g),2)]
layers=load('mixed36.json')
assert len(layers)==3
players=set()
for h,layer in enumerate(layers):
    group=set(sum(layer[0],[]))
    assert len(group)==12 and not players&group and len(layer)==11
    players|=group
    assert all(sorted(sum(w,[]))==sorted(group) for w in layer)
    counts=Counter(p for w in layer for p in edges(w))
    assert len(counts)==66 and set(counts.values())=={2}
    for a,b in [(0,3),(3,7),(7,11)]:
        hits=[p for w in layer[a:b] for p in edges(w)]
        assert len(hits)==len(set(hits))
    choices=load(f'subclasses{h}.json')
    for n,options in choices.items():
        for mask,ids in options:
            weeks=[u//4 for u in ids]
            bowlers=[x for u in ids for x in layer[u//4][u%4]]
            assert len(ids)==len(set(weeks))==int(n)
            assert len(bowlers)==len(set(bowlers))
            assert mask==sum(1<<w for w in weeks)
assert players==set(range(1,37))
fixed=load('fixed_first_round.json')['weeks']
tail=[p for row in fixed[-9:] for p in edges([row[i:i+3] for i in range(0,36,3)])]
bridge=[p for layer in layers for w in layer[:3] for p in edges(w)]
assert len(set(tail+bridge))==len(tail+bridge)==432
print('Three disjoint layers, 198 within-layer couples meeting twice, 12 clash-free boundary weeks, and all candidate lane fragments verified.')
