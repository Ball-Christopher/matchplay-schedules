import itertools, random
def lanes12(W, rng, limit=400000):
    """W: 11 weeks of 3 groups. DFS over group orders so total lane excess <= 1. Returns (exc, W') or None."""
    P=list(itertools.permutations(range(3)));cnt=[[0]*3 for _ in range(13)];out=[None]*11;nodes=[0]
    order=list(range(11))
    def rec(k,over):
        nodes[0]+=1
        if nodes[0]>limit:return None
        if k==11:
            exc=sum(max(0,c-4)+max(0,3-c) for p in range(1,13) for c in cnt[p]);return exc if exc<=1 else None
        rem=10-k;wk=W[order[k]]
        for pm in (P if k else P[:1]):
            o=over
            for l in range(3):
                for p in wk[pm[l]]:
                    cnt[p][l]+=1
                    if cnt[p][l]>4:o+=1
            ok=o<=1
            if ok:
                und=0
                for p in range(1,13):
                    for c in cnt[p]:
                        if c+rem<3:und+=3-c-rem
                ok=o+und<=1
            if ok:
                out[order[k]]=[wk[pm[l]] for l in range(3)]
                r=rec(k+1,o)
                if r is not None:return r
            for l in range(3):
                for p in wk[pm[l]]:cnt[p][l]-=1
        return None
    r=rec(0,0)
    return (r,[list(x) for x in out]) if r is not None else None
