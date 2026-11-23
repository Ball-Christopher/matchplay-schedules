import json, itertools, os
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
V = 18
d = json.load(open(os.path.join(HERE, '../../../v18_oil.json')))
R1 = [[w[i:i+3] for i in range(0, 18, 3)] for w in d['weeks']]      # round 1, 1-based, with positions
def pairs(wk): return [tuple(sorted(x)) for g in wk for x in itertools.combinations(g, 2)]
ALLP = list(itertools.combinations(range(1, V + 1), 2))
A, B, C = R1[:8], R1[8:13], R1[13:]
F = sorted(set(ALLP) - set(p for wk in A for p in pairs(wk)))
CP = set(p for wk in C for p in pairs(wk))                            # pairs used in v18_oil's last block
R1T = set(tuple(sorted(g)) for wk in R1 for g in wk)                  # round-1 trios
pos = Counter((p, q) for wk in R1 for g in wk for q, p in enumerate(g))
SHORT = {p: next(q for q in range(3) if pos[p, q] == 5) for p in range(1, V + 1)}  # position each bowler is owed
LANE1 = Counter((p, l) for wk in R1 for l, g in enumerate(wk) for p in g)
