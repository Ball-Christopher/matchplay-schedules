"""Generate every admissible internal lane fragment of size four."""
from itertools import combinations
from pathlib import Path
import json

def maximum_disjoint(fragments):
    if not fragments:
        return 0
    first, *rest = fragments
    return max(maximum_disjoint(rest),
               1 + maximum_disjoint([other for other in rest if not first & other]))

path = Path(__file__).resolve().parents[1] / 'inputs/mixed36.json'
results = []
for layer in json.loads(path.read_text()):
    groups = [set(group) for week in layer for group in week]
    fragments = []
    for indices in combinations(range(44), 4):
        if len({i // 4 for i in indices}) != 4:
            continue
        if len(set.union(*(groups[i] for i in indices))) == 12:
            fragments.append(sum(1 << i for i in indices))
    results.append((len(fragments), maximum_disjoint(fragments)))
assert results == [(27, 8), (12, 5), (27, 8)]
print('Four-triple fragment counts and maximum disjoint subfamilies:', results)
