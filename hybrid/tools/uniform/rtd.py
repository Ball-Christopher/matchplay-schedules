"""Resolvable transversal designs RTD(4,q) over GF(q) with the groups filled in.

RTD(4,q): points (i, y), i = 0..3 (groups), y in GF(q); blocks {(i, a + b*e_i)} with
e_0..e_3 distinct field elements; fixing b gives a parallel class (a = 0..q-1).
  v=36: RTD(4,9) + each group of 9 filled with KTS(9) = AG(2,3)        -> 0-4-9
  v=32: RTD(4,8) + each group of 8 filled with 2 K4s (one 4-way class)
        and K_{4,4} as 4 matchings                                         -> 4-0-9
Points are numbered 1 + i*q + y."""
import itertools

def gf(q):
    """add, mul tables for q in {2,3,4,5,7,8,9}."""
    if q in (2, 3, 5, 7):
        return [[(a + b) % q for b in range(q)] for a in range(q)], [[(a * b) % q for b in range(q)] for a in range(q)]
    p, n, poly = {4: (2, 2, (1, 1)), 8: (2, 3, (1, 1, 0)), 9: (3, 2, (2, 0))}[q]  # x^n = sum poly[i] x^i
    def dig(a): return [(a // p ** i) % p for i in range(n)]
    def und(d): return sum(x * p ** i for i, x in enumerate(d))
    def mul(a, b):
        A, B = dig(a), dig(b); c = [0] * (2 * n)
        for i in range(n):
            for j in range(n): c[i + j] = (c[i + j] + A[i] * B[j]) % p
        for k in range(2 * n - 1, n - 1, -1):
            t = c[k]; c[k] = 0
            for i in range(n): c[k - n + i] = (c[k - n + i] + t * poly[i]) % p
        return und(c[:n])
    add = [[und([(x + y) % p for x, y in zip(dig(a), dig(b))]) for b in range(q)] for a in range(q)]
    return add, [[mul(a, b) for b in range(q)] for a in range(q)]

def rtd4(q, e=(0, 1, 2, 3)):
    add, mul = gf(q)
    return [[[1 + i * q + add[a][mul[b][e[i]]] for i in range(4)] for a in range(q)] for b in range(q)]

def v36_049():
    W = rtd4(9)
    # AG(2,3) on GF(9) viewed as GF(3)^2: lines = cosets of the 4 one-dim subspaces
    dirs = [(1, 0), (0, 1), (1, 1), (1, 2)]
    def pt(x, y): return x + 3 * y        # GF(9) element with digits (x, y)
    for dx, dy in dirs:
        wk = []
        for i in range(4):
            seen = set()
            for x0, y0 in itertools.product(range(3), repeat=2):
                L = tuple(sorted(pt((x0 + t * dx) % 3, (y0 + t * dy) % 3) for t in range(3)))
                if L not in seen: seen.add(L); wk.append([1 + i * 9 + y for y in L])
        W.append(wk)
    return W

def v32_409():
    W = rtd4(8)
    W.append([[1 + i * 8 + y for y in h] for i in range(4) for h in ((0, 1, 2, 3), (4, 5, 6, 7))])
    for s in range(4):
        W.append([[1 + i * 8 + x, 1 + i * 8 + 4 + (x + s) % 4] for i in range(4) for x in range(4)])
    return W

if __name__ == '__main__':
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from common import check_design
    check_design(36, v36_049()); check_design(32, v32_409()); print('ok')
