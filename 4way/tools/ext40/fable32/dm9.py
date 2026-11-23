# Is there a set of 8 (hence 9) pairwise type-disjoint transversal weeks over Z_9 x 4, i.e. a (9,4;1) difference matrix over Z_9?
import itertools
orth = [p for p in itertools.permutations(range(9)) if p[0] == 0 and len({(p[a] - a) % 9 for a in range(9)}) == 9]
print("orthomorphisms fixing 0:", len(orth))
n = 0
for b in orth:
    for c in itertools.permutations(range(9)):
        pass
        break
# c must be a permutation with c-a and c-b permutations; c[0] free
import sys
def ext(b):
    out = 0
    def rec(a, c, uc, ua, ub):
        nonlocal out
        if a == 9: out += 1; return
        for x in range(9):
            if uc >> x & 1: continue
            d1 = (x - a) % 9; d2 = (x - b[a]) % 9
            if ua >> d1 & 1 or ub >> d2 & 1: continue
            rec(a + 1, c + [x], uc | 1 << x, ua | 1 << d1, ub | 1 << d2)
    rec(0, [], 0, 0, 0); return out
print("orthogonal pairs:", sum(ext(b) for b in orth))
