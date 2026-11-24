"""Enumerate all ways to keep three of seven weeks and refill the other four."""
from itertools import combinations
from pathlib import Path
from collections import Counter
import json

ROOT=Path(__file__).resolve().parent
PAIRS=list(combinations(range(24),2))
EDGE={pair:1<<i for i,pair in enumerate(PAIRS)}
def members(mask):
    while mask:
        bit=mask&-mask
        yield bit.bit_length()-1
        mask^=bit
def pairs(group):return sum(EDGE[e] for e in combinations(members(group),2))
def normalize(weeks):return tuple(sorted(tuple(sorted(w)) for w in weeks))

def seed():
    data=json.loads((ROOT/'v24_0-1-7.json').read_text())
    weeks=[tuple(sum(1<<(x-1) for x in g) for g in w if g) for w in data['weeks']]
    return normalize(w for w in weeks if len(w)==6)

def completions(keep):
    occupied=0
    for w in keep:
        for g in w:occupied|=pairs(g)
    containing=[[] for _ in range(24)]
    for quartet in combinations(range(24),4):
        group=sum(1<<x for x in quartet)
        edges=pairs(group)
        if occupied&edges:continue
        for x in quartet:containing[x].append((group,edges))
    candidates=[]
    def one_week(players,groups,edges):
        if not players:
            candidates.append((groups,edges));return
        pivot=(players&-players).bit_length()-1
        for g,e in containing[pivot]:
            if g&players==g:one_week(players^g,groups+(g,),edges|e)
    one_week((1<<24)-1,(),0)
    count=len(candidates);width=(count+7)//8
    incidence=[bytearray(width) for _ in PAIRS]
    for i,(_,edges) in enumerate(candidates):
        for e in members(edges):incidence[e][i//8]|=1<<(i%8)
    hits=[int.from_bytes(b,'little') for b in incidence]
    compatible=[]
    for _,edges in candidates:
        clashes=0
        for e in members(edges):clashes|=hits[e]
        compatible.append(~clashes)
    found=[]
    def choose(pool,selected):
        if len(selected)==4:
            found.append(normalize((*keep,*(candidates[i][0] for i in selected))))
            return
        while pool:
            i=(pool&-pool).bit_length()-1
            pool^=1<<i
            choose(pool&compatible[i],selected+(i,))
    choose((1<<count)-1,())
    return count,found

def relabel(weeks,image):
    return normalize(tuple(sum(1<<image[x] for x in members(g)) for g in w) for w in weeks)

if __name__=='__main__':
    original=seed()
    maps=json.loads((ROOT/'isomorphisms.json').read_text())
    neighbours=set()
    for keep in combinations(original,3):
        n,found=completions(keep)
        assert original in found
        neighbours.update(set(found)-{original})
        print([original.index(w)+1 for w in keep],n,len(found),flush=True)
    assert len(neighbours)==len(maps)==7
    for item in maps:
        alt=normalize(item['alternative'])
        assert alt in neighbours and len(set(original)&set(alt))==3
        assert sorted(item['player_image'])==list(range(24))
        assert relabel(original,item['player_image'])==alt
    assert {normalize(m['alternative']) for m in maps}==neighbours
    all_used=[e for w in original for g in w for e in combinations(members(g),2)]
    assert len(set(all_used))==len(all_used)==252
    unseen=set(PAIRS)-set(all_used)
    triangles=[g for g in combinations(range(24),3) if set(combinations(g,2))<=unseen]
    assert len(triangles)==8 and len(set(sum(triangles,())))==24
    print('Seven labelled neighbours. Every neighbour is isomorphic to the seed.')
