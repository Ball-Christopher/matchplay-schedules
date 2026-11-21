import json, random, sys, itertools
from collections import Counter
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[4] / 'tools'))
from positions import assign
d=json.load(open('z8_1_3.json')); A,B,I,IZ=d['A'],d['B'],d['I'],d['IZ']
sh=lambda p,k:(p//8)*8+(p%8+k)%8
random.seed(5)
def build(lA,lB,s):
    # returns dict name->week (list of 8 groups by lane)
    W={}
    for nm,base,lam in (('A',A,lA),('B',B,lB)):
        for i in range(8):
            wk=[None]*8
            for g,t in enumerate(base): wk[(lam[g]+i)%8]=[sh(p,i) for p in t]
            W[nm,i]=wk
    for t,(a,b) in enumerate(I):
        wk=[None]*8
        for i in range(8): wk[(i+s[t])%8]=[i,8+(i+a)%8,16+(i+b)%8]
        W['I',t]=wk
    return W
def cost(W):
    c=Counter()
    for wk in W.values():
        for l,g in enumerate(wk):
            for p in g: c[p,l]+=1
    return sum(1 for p in range(24) for l in range(8) if not 2<=c[p,l]<=3)
lA,lB,s=[[6, 5, 1, 0, 7, 4, 2, 3], [5, 1, 3, 4, 7, 2, 0, 6], [2, 3, 6, 3, 1, 4, 7]]
it=0
assert cost(build(lA,lB,s))==0
print('lane iters',it,lA,lB,s)
W=build(lA,lB,s)
IX=[t for t in range(7) if t not in IZ]
order=[('B',i) for i in range(8)]+[('I',t) for t in IZ]+[('A',i) for i in range(4)]+[('I',t) for t in IX[:2]]+[('A',i) for i in range(4,8)]+[('I',t) for t in IX[2:]]
blocks=[11,6,6]
weeks=[W[k] for k in order]
weeks=assign(weeks,3)
flat=[[p+1 for g in wk for p in g] for wk in weeks]
# checks
m=Counter()
for w in flat:
    for g in range(8):
        for a,b in itertools.combinations(sorted(w[3*g:3*g+3]),2): m[a,b]+=1
assert len(m)==276 and set(m.values())=={2}
st=0
for bl in blocks:
    mm=Counter()
    for w in flat[st:st+bl]:
        for g in range(8):
            for a,b in itertools.combinations(sorted(w[3*g:3*g+3]),2): mm[a,b]+=1
    assert max(mm.values())==1; st+=bl
fmt=lambda base:' '.join('{'+','.join(f"{'abc'[p//8]}{p%8}" for p in t)+'}' for t in base)
method=("Points Z_8 x {a,b,c} with automorphism i -> i+1. Two base weeks A0 = "+fmt(A)+" and B0 = "+fmt(B)+
 " developed mod 8, plus 7 invariant weeks {a_i, b_(i+x), c_(i+y)} for (x,y) = "+' '.join(f"({a},{b})" for a,b in I)+
 ". B0 and each of A0's non-antipodal pairs use distinct pair-orbits, so the 8 B weeks are clash-free and A_i clashes only with A_(i+4); "
 "blocks = B0-7 + 3 invariant weeks (11, a nearly Kirkman triple system leaving the antipodal pairs {i,i+4}), A0-3 + 2 invariant, A4-7 + 2 invariant. "
 "Base weeks found by backtracking over pair-orbit capacities; lanes rotate with the automorphism (group on lane g moves to lane g+1), base lane labels by hill-climb, giving exact lane balance; "
 "biggest block first so only weeks 12-14 sit at prefix spread 2; positions by de Werra edge colouring")
out={"players":24,"group":3,"rounds":1,"lambda":2,"weeks":flat,"blocks":blocks,"lane_balance_exact":True,"method":method}
json.dump(out,open('v24_oil.json','w'))
ps=[];m=Counter();cp=list(itertools.combinations(range(1,25),2))
for w in flat:
    for g in range(8):
        for a,b in itertools.combinations(sorted(w[3*g:3*g+3]),2): m[a,b]+=1
    v=[m[c] for c in cp]; ps.append(max(v)-min(v))
print(ps)
L=["# 24 bowlers, groups of 3, 23 weeks, every couple meets exactly twice.",
"# Oil-pattern blocks (weeks, in order): [11, 6, 6] -- block 1 = weeks 1-11, block 2 = weeks 12-17, block 3 = weeks 18-23.",
"# Within a block no couple shares a group twice, so each couple meets on 2 different patterns.",
f"# Lane pairs = consecutive groups of 3 in each week; lane balance exact: true. Worst prefix spread {max(ps[:-1])}.",
"# Method: "+method,"[schedule]","weeks = ["]+["  "+json.dumps(w)+"," for w in flat]+["]"]
open('v24_oil.toml','w').write('\n'.join(L)+'\n')
