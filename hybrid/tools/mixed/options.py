"""List fair mixes (a2,a3,a4) with R<=16 for given v, and the week-type multisets that realise them.
A week type is (g2,g3,g4) = numbers of 2-,3-,4-groups. Usage: python3 options.py 11 13 ..."""
import sys, itertools
def wtypes(v):
    return [(g2,g3,g4) for g4 in range(v//4+1) for g3 in range(v//3+1)
            for g2 in [(v-3*g3-4*g4)//2] if g2 >= 0 and 2*g2+3*g3+4*g4 == v]
def solutions(v, R, a, limit=50):
    T = wtypes(v); tgt = (v*a[0]//2, v*a[1]//3, v*a[2]//4)
    if v*a[0] % 2 or v*a[1] % 3 or v*a[2] % 4: return []
    out = []
    def rec(i, left, acc, cur):
        if len(out) >= limit: return
        if i == len(T):
            if left == 0 and acc == tgt: out.append(tuple(cur))
            return
        t = T[i]
        for k in range(left+1):
            nacc = tuple(acc[j]+k*t[j] for j in range(3))
            if any(nacc[j] > tgt[j] for j in range(3)): break
            cur.append((t, k)); rec(i+1, left-k, nacc, cur); cur.pop()
    rec(0, R, (0,0,0), [])
    return [[(t,k) for t,k in s if k] for s in out]
def mixes(v):
    for a4 in range((v-1)//3+1):
        for a3 in range((v-1-3*a4)//2+1):
            a2 = v-1-3*a4-2*a3; R = a2+a3+a4
            if R <= int(__import__("os").environ.get("RMAX", "16")):
                s = solutions(v, R, (a2,a3,a4))
                if s: yield R, (a2,a3,a4), s
if __name__ == "__main__":
    for v in map(int, sys.argv[1:]):
        print(f"v={v}")
        for R, a, s in sorted(mixes(v)):
            mixed = [x for x in s if any(sum(1 for c in t if c) > 1 for t, k in x)]
            print(f"  R{R} {a}: {len(s)} type-multisets ({len(mixed)} with mixed weeks); e.g. {s[0]}")
