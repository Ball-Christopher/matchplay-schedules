"""Check both complete schedules, their fixed first rounds, and the qualifying witness."""
from pathlib import Path
from itertools import combinations
from collections import Counter
import json
import sys

ROOT=Path(__file__).resolve().parent

def check_round(weeks, multiplicity):
    meetings, lanes, positions = Counter(), Counter(), Counter()
    current, runs = set(), []
    for row in weeks:
        assert sorted(row) == list(range(1,25))
        edges = {pair for j in range(0,24,3)
                 for pair in combinations(sorted(row[j:j+3]),2)}
        if not runs or current & edges:
            current.clear()
            runs.append(0)
        runs[-1] += 1
        current.update(edges)
        meetings.update(edges)
        for j, player in enumerate(row):
            lanes[player,j//3] += 1
            positions[player,j%3] += 1
    assert len(meetings)==276 and set(meetings.values())=={multiplicity}
    for counts, n in ((lanes,8),(positions,3)):
        for p in range(1,25):
            totals=[counts[p,j] for j in range(n)]
            assert max(totals)-min(totals)<=1
    return runs

def main():
    if not __debug__: raise RuntimeError('Run Python without -O.')
    for name,file in [('oil','v24_oil'),('main','v24')]:
        data=json.loads((ROOT/'3way'/f'{file}_x2.json').read_text())
        weeks=data['weeks']
        assert len(weeks)==46
        first=json.loads((ROOT/'inputs'/f'first_{name}.json').read_text())['weeks']
        assert weeks[:23]==first
        if len(sys.argv)>1:
            ref=Path(sys.argv[1])/'3way'/f'{file}.json'
            assert first==json.loads(ref.read_text())['weeks']
        before=check_round(first,2)
        check_round(weeks[23:],2)
        cuts=check_round(weeks,4)
        lower=len(before)-1+(before[-1]+23+10)//11
        assert cuts==data['blocks'] and len(cuts)==lower
        start=23
        for length in (2,10,11):
            pairs=[p for w in weeks[start:start+length] for j in range(0,24,3)
                   for p in combinations(sorted(w[j:j+3]),2)]
            assert len(pairs)==len(set(pairs))
            start+=length
        print(name, 'optimal', lower, 'pattern lengths', cuts)
    d=json.loads((ROOT/'qualifying15/published_draw.json').read_text())
    lanes, meetings, follows=Counter(),Counter(),Counter()
    for week in d['draw']:
        assert len(week)==5 and sorted(sum(week,[]))==list(range(1,16))
        for lane,g in enumerate(week):
            assert len(g)==3
            lanes.update((p,lane) for p in g)
            meetings.update(combinations(sorted(g),2))
            cycle=g[::2]+g[1::2]
            follows.update(zip(cycle,cycle[1:]+cycle[:1]))
    assert len(d['draw'])==6 and len(lanes)==75 and set(lanes.values())=={1,2}
    assert max(meetings.values())==2 and max(follows.values())==1
    print('15 qualifying: balanced witness with meeting and follow maxima (2, 1)')

if __name__=='__main__':main()
