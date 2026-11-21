import json, random, math
d=json.load(open('z8_1_3.json')); A,B,I=d['A'],d['B'],d['I']
def cost(lA,lB,s):
    M=[[0]*8 for _ in range(3)]
    for base,lam in ((A,lA),(B,lB)):
        for g,t in enumerate(base):
            for p in t: M[p//8][(lam[g]-p)%8]+=1
    for t,(a,b) in enumerate(I):
        M[0][s[t]%8]+=1; M[1][(s[t]-a)%8]+=1; M[2][(s[t]-b)%8]+=1
    return sum((x-2)*(x-3) for r in M for x in r)
for seed in range(50):
    random.seed(seed)
    lA=list(range(8)); lB=list(range(8)); s=[0]*7; random.shuffle(lA); random.shuffle(lB)
    cur=cost(lA,lB,s); T=2.0
    for it in range(200000):
        if cur==0: break
        T=max(0.3,T*0.99997)
        nA,nB,ns=lA[:],lB[:],s[:]
        r=random.random()
        if r<0.4: i,j=random.sample(range(8),2); nA[i],nA[j]=nA[j],nA[i]
        elif r<0.8: i,j=random.sample(range(8),2); nB[i],nB[j]=nB[j],nB[i]
        else: ns[random.randrange(7)]=random.randrange(8)
        c=cost(nA,nB,ns)
        if c<=cur or random.random()<math.exp((cur-c)/T): lA,lB,s,cur=nA,nB,ns,c
    print(seed,cur,flush=True)
    if cur==0: print(json.dumps([lA,lB,s])); break
