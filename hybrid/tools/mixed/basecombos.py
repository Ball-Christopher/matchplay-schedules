"""Base week type combos: basecombos.py v m nbase tot2 tot3 tot4 (group totals left for base weeks, already divided by m)"""
import sys, itertools
from options import wtypes
v, m, nb, t2, t3, t4 = map(int, sys.argv[1:])
for comb in itertools.combinations_with_replacement(wtypes(v), nb):
    if tuple(map(sum, zip(*comb))) == (t2, t3, t4): print(" ".join(f"F:{a},{b},{c}" for a, b, c in comb))
