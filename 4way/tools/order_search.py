"""Order weeks so every prefix has small couple-meeting spread (beam search)."""
import json, sys
from itertools import combinations
def pairsets(v, weeks):
    idx = {p:i for i,p in enumerate(combinations(range(1,v+1),2))}
    return [[idx[(a,b)] for g in w for a,b in combinations(sorted(g),2)] for w in weeks], len(idx)
def beam_order(v, weeks, beam=200, first=0):
    ps, np_ = pairsets(v, weeks)
    n = len(weeks)
    c0 = [0]*np_
    for i in ps[first]: c0[i]+=1
    states = [((max(c0)-min(c0),), [first], c0)]
    for step in range(1, n):
        cand = []
        for hist, seq, c in states:
            used = set(seq)
            for j in range(n):
                if j in used: continue
                c2 = c[:]
                for i in ps[j]: c2[i]+=1
                mx, mn = max(c2), min(c2)
                s = mx-mn
                # secondary: number of pairs at extremes (fewer at max / min is better)
                hi = c2.count(mx); lo = c2.count(mn)
                worst = max(max(hist), s)
                cand.append(((worst, s, min(hi,lo)), hist+(s,), seq+[j], c2))
        cand.sort(key=lambda x: x[0])
        seen=set(); states=[]
        for key,hist,seq,c in cand:
            k=tuple(sorted(seq))
            if k in seen: continue
            seen.add(k); states.append((hist,seq,c))
            if len(states)>=beam: break
    hist, seq, c = min(states, key=lambda s:(max(s[0]), sum(s[0])))
    return seq, list(hist)
if __name__=="__main__":
    D = json.load(open("designs_raw.json"))
    for v in sys.argv[1:]:
        seq,h = beam_order(int(v), D[v]["weeks"], beam=int(400))
        print(v, seq, h)
