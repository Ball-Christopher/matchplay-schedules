"""Exhaust all possible continuations of the fixed tails in three foursome cases."""
from itertools import combinations
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
def edges(row):
    return {pair for j in range(0,len(row),4) for pair in combinations(sorted(row[j:j+4]),2)}
def continuations(weeks, number):
    players=tuple(sorted(weeks[0]))
    occupied=set.union(*(edges(w) for w in weeks))
    groups=[(set(g),set(combinations(g,2))) for g in combinations(players,4) if not set(combinations(g,2))&occupied]
    def cover(remaining,selected,previous,depth):
        if not remaining:
            if depth==number:return 1
            return cover(set(players),[],previous|set.union(*(e for _,e in selected)),depth+1)
        choices=min(([g for g in groups if x in g[0] and g[0]<=remaining and not g[1]&previous] for x in remaining),key=len)
        return sum(cover(remaining-g[0],selected+[g],previous,depth) for g in choices)
    return len(groups),cover(set(players),[],set(),1)
for name,tail,h,expected in [('4w24_main',5,2,60),('4w32_main',8,1,7),('4w32_oil',8,1,7)]:
    d=json.loads((root/'two_rounds'/(name+'.json')).read_text());r=d['players']-1
    count,ways=continuations(d['weeks'][r-tail:r],h)
    assert count==expected and ways==0
    print(name,count,'possible first quartets,',ways,'valid continuations of length',h)
