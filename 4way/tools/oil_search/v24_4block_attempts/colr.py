import sys, itertools, random
from z3 import *
idx=int(sys.argv[1]); sizes=[int(c) for c in sys.argv[2]]; mode=sys.argv[3]
lines=open('allbase.txt').read().splitlines()
random.seed(idx); line=lines[random.randrange(len(lines)-1)]
v=[int(x) for x in line.split()]
base=[v[i:i+4] for i in range(0,24,4)]
def sh(x,t): return 23 if x==-1 else (x+t)%23
blocks=[tuple(sorted(sh(x,t) for x in b)) for b in base for t in range(23)]
y=[[Bool(f"y{b}_{c}") for c in range(4)] for b in range(138)]
s=Solver(); s.set("timeout",120000)
for b in range(138): s.add(PbEq([(y[b][c],1) for c in range(4)],1))
for p,q in itertools.combinations(range(24),2):
    bs=[b for b in range(138) if p in blocks[b] and q in blocks[b]]
    for c in range(4):
        for a,b in itertools.combinations(bs,2): s.add(Or(Not(y[a][c]),Not(y[b][c])))
if mode=='deg':
    for p in range(24):
        bs=[b for b in range(138) if p in blocks[b]]
        for c in range(4): s.add(PbEq([(y[b][c],1) for b in bs],sizes[c]))
if mode=='le':
    for p in range(24):
        bs=[b for b in range(138) if p in blocks[b]]
        for c in range(4): s.add(PbLe([(y[b][c],1) for b in bs],7))
print(idx,mode,s.check())
