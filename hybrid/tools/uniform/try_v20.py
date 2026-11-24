"""v20 (4,0,5): Z_5 x 4 rows, one base 4-way class developed mod 5 (5 weeks); the four
2-way weeks are fixed, each the union of two mixed-difference orbits on complementary
row pairs.  Random choices of those orbits, short C search for each."""
import os, sys, random, time, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cyclic import search_c
from try_rows import mixed_match
rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
PAIRINGS = [((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2))]
t0 = time.time()
while time.time() - t0 < float(os.environ.get('TL', 300)):
    used = set(); fx = []
    for _ in range(4):
        for _ in range(50):
            (a, b), (c, d) = rng.choice(PAIRINGS); d1, d2 = rng.randrange(5), rng.randrange(5)
            if (a, b, d1) not in used and (c, d, d2) not in used: break
        used |= {(a, b, d1), (c, d, d2)}; fx.append(mixed_match(5, a, b, d1) + mixed_match(5, c, d, d2))
    if len(used) < 8: continue
    W = search_c(5, 4, 0, [4], fx, seed=rng.randrange(10**6), node_limit=200000, time_limit=3)
    if W:
        print('v20_405 found', round(time.time() - t0, 1)); print(W); break
else:
    print('v20_405 NOT found')
