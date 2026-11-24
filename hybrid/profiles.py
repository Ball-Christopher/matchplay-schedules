# Fair hybrid single rounds (couples meet once; every bowler gets the same number
# a2,a3,a4 of 2-, 3- and 4-way weeks). Checks that week types can realise the slot totals.
import itertools, json
def wtypes(v):
    return [(g2,g3,g4) for g4 in range(v//4+1) for g3 in range(v//3+1)
            for g2 in [(v-3*g3-4*g4)//2] if g2 >= 0 and 2*g2+3*g3+4*g4 == v]
def realisable(v, R, a):
    T = wtypes(v); target = (2*0+v*a[0], v*a[1], v*a[2])  # slots in 2-,3-,4-groups
    # DP over number of weeks and slot vectors
    S = {(0,0,0)}
    for _ in range(R):
        S = {(x+2*t[0], y+3*t[1], z+4*t[2]) for (x,y,z) in S for t in T
             if x+2*t[0] <= target[0] and y+3*t[1] <= target[1] and z+4*t[2] <= target[2]}
    return target in S
pure = {3: lambda v: v % 6 == 3, 4: lambda v: v % 12 == 4, 2: lambda v: v % 2 == 0}
res = {}
for v in range(11, 41):
    rows = []
    for a4 in range((v-1)//3+1):
        for a3 in range((v-1-3*a4)//2+1):
            a2 = v-1-3*a4-2*a3; R = a2+a3+a4
            if R > 16 or not realisable(v, R, (a2,a3,a4)): continue
            kinds = sum(1 for a in (a2,a3,a4) if a)
            uniform = all(a == 0 or v % s == 0 for s,a in ((2,a2),(3,a3),(4,a4)))
            rows.append((R, a2, a3, a4, kinds, uniform))
    res[v] = sorted(rows)
    hyb = [r for r in res[v] if r[4] > 1]
    pures = [f"{s}-way R{(v-1)//(s-1)}" for s in (2,3,4) if pure[s](v)]
    print(f"{v:2d} pure:{','.join(pures) or '-':22s} hybrid R range {min(r[0] for r in hyb) if hyb else '-'}-{max(r[0] for r in hyb) if hyb else '-'}; "
          + "; ".join(f"R{R}:{a2}/{a3}/{a4}{'' if u else '*'}" for R,a2,a3,a4,k,u in hyb[:5]))
json.dump({v: r for v, r in res.items()}, open('profiles.json','w'))
