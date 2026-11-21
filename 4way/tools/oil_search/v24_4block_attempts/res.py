import sys, itertools, random, json
from z3 import *
# args: line index in allbase.txt, sizes e.g. 6665, timeout s
idx=int(sys.argv[1]); sizes=[int(c) for c in sys.argv[2]]; to=int(sys.argv[3])
lines=open('allbase.txt').read().splitlines()
random.seed(idx); line=lines[random.randrange(len(lines)-1)]
v=[int(x) for x in line.split()]
base=[v[i:i+4] for i in range(0,24,4)]
def sh(x,t): return 23 if x==-1 else (x+t)%23
blocks=[tuple(sorted(sh(x,t) for x in b)) for b in base for t in range(23)]
assert len(set(blocks))==138
col=[c for c,s in enumerate(sizes) for _ in range(s)]
W=23
x=[[Bool(f"x{b}_{w}") for w in range(W)] for b in range(138)]
y=[[Bool(f"y{b}_{c}") for c in range(4)] for b in range(138)]
s=Solver(); s.set("timeout",to*1000)
for b in range(138):
    s.add(PbEq([(x[b][w],1) for w in range(W)],1))
    for c in range(4):
        s.add(y[b][c]==Or([x[b][w] for w in range(W) if col[w]==c]))
for p in range(24):
    bs=[b for b in range(138) if p in blocks[b]]
    for w in range(W): s.add(PbEq([(x[b][w],1) for b in bs],1))
for p,q in itertools.combinations(range(24),2):
    bs=[b for b in range(138) if p in blocks[b] and q in blocks[b]]
    assert len(bs)==3
    for c in range(4):
        for a,b in itertools.combinations(bs,2): s.add(Or(Not(y[a][c]),Not(y[b][c])))
s.add(x[0][0])
r=s.check()
print(idx,line,r,flush=True)
if r==sat:
    m=s.model()
    weeks=[[blocks[b] for b in range(138) if is_true(m[x[b][w]])] for w in range(W)]
    json.dump({'sizes':sizes,'weeks':weeks},open(f'found_{idx}_{sys.argv[2]}.json','w'))
