"""Test all seven KTS(15) representatives and each deletion of a parallel class."""
from itertools import combinations, product
from pathlib import Path
import json
def balanced_assignment(weeks):
    groups=[[sum(1<<p for p in triple) for triple in week] for week in weeks]
    choices=[[] for _ in range(5)]
    for lane in product(range(5),repeat=len(weeks)):
        once=twice=group_mask=0
        for t,j in enumerate(lane):
            group=groups[t][j]
            if twice&group:break
            twice|=once&group
            once|=group
            group_mask|=1<<(5*t+j)
        else:
            if once==(1<<15)-1:choices[lane[0]].append(group_mask)
    def cover(i,used):
        return i==5 or any(cover(i+1,used|m) for m in choices[i] if not m&used)
    return cover(0,0)
cases=json.loads(Path(__file__).with_name('k15_reps.json').read_text())
assert len(cases)==7
for i,weeks in enumerate(cases,1):
    assert all(sorted(sum(w,[]))==list(range(15)) for w in weeks)
    assert len({tuple(sorted(e)) for w in weeks for g in w for e in combinations(g,2)})==105
    assert not balanced_assignment(weeks)
    for j in range(7):assert not balanced_assignment(weeks[:j]+weeks[j+1:])
    print('Representative',i,'passed the full and seven deletion checks')
