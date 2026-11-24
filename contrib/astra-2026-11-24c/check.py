"""Run with Python 3 and assertions enabled, optionally providing a repository checkout."""
from collections import Counter
from itertools import combinations
from pathlib import Path
import json
import sys
from upstream.hybrid_verify import check as hybrid_check
from upstream.model import evaluate, SCORE_FIELDS

root = Path(__file__).resolve().parent
def read(name):
    return json.loads((root / name).read_text())

def matchplay(weeks, expected):
    pairs, lanes, positions = Counter(), Counter(), Counter()
    blocks, current = [], set()
    for row in weeks:
        assert sorted(row) == list(range(1, 37))
        opponents = {pair for i in range(0, 36, 3)
                     for pair in combinations(sorted(row[i:i+3]), 2)}
        if not blocks or opponents & current:
            blocks.append(0)
            current.clear()
        blocks[-1] += 1
        current.update(opponents)
        pairs.update(opponents)
        for i, x in enumerate(row):
            lanes[x, i//3] += 1
            positions[x, i%3] += 1
    assert len(pairs) == 630 and set(pairs.values()) == {expected}
    for x in range(1, 37):
        for counts, size in ((lanes,12),(positions,3)):
            visits = [counts[x,i] for i in range(size)]
            assert max(visits)-min(visits) <= 1
    return blocks

def main():
    assert __debug__, 'Use Python without -O'
    schedule = read('3way/v36_oil_x2.json')
    weeks = schedule['weeks']
    fixed = read('inputs/fixed36_oil.json')['weeks']
    assert len(weeks) == 70 and weeks[:35] == fixed
    if len(sys.argv)>1:
        upstream = Path(sys.argv[1])/'3way/v36_oil.json'
        assert weeks[:35] == json.loads(upstream.read_text())['weeks']
    assert matchplay(weeks[:35], 2) == [16,10,9]
    assert matchplay(weeks[35:], 2) == [3,16,16]
    assert matchplay(weeks, 4) == schedule['blocks'] == [16,10,12,16,16]
    print('36 trios: fixed first round; balanced halves and season; 5 patterns.')
    d = read('qualifying/M3_K4_B11.json')
    assert len(d['draw']) == 11
    for w in d['draw']:
        assert len(w)==3 and all(len(g)==4 for g in w)
        assert sorted(sum(w,[])) == list(range(1,13))
    assessment = evaluate([[[x-1 for x in g] for g in w] for w in d['draw']])
    assert assessment['score'] == (1,4,1,132,0,2,66,-2,1,1)
    assert d['score'] == dict(zip(SCORE_FIELDS, assessment['score']))
    print('12 qualifying: all 132 directed follows exactly once; all ten score fields verified.')
    for n, r in [(27,9),(39,13)]:
        info = hybrid_check(root/'hybrid'/f'v{n}_0-1-{r-1}_mixed.json')
        assert info['valid'] and info['weeks']==r and info['mix_2_3_4']==[(0,1,r-1)]
        assert info['lane_off_bowlers']==info['position_off']==0
        parent = read(f'inputs/four{n+1}.json')['weeks']
        child = read(f'hybrid/v{n}_0-1-{r-1}_mixed.json')['weeks']
        assert len(parent) == len(child)
        for row, week in zip(parent, child):
            assert [set(row[i:i+4])-{n+1} for i in range(0,n+1,4)] == [set(g) for g in week]
        print(f'{n} hybrid: {r} weeks; one meeting per pair; exact lanes and balanced positions.')

if __name__ == '__main__':
    main()
