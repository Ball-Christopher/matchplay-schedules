"""Algebraic zero-repeat designs used as starting points for the anneal.

Field construction (resolvable transversal design over GF(q), q = M a prime
power, K <= M): bowler (i, v) with type i < K and v in GF(q).  In round x the
pair a holds the bowlers (i, a + e_i * x), i = 0..K-1, with e_i distinct field
elements.  Two bowlers of types i != j meet in round x iff
v_i - v_j = (e_i - e_j) x, which has exactly one solution x, so the q rounds
have no repeated couple.  When K = M one more round is available: the K
bowlers of each type together (this completes the affine plane AG(2, q)).
For prime q this is exactly the movement rule "type i moves -e_i pairs".
"""
from __future__ import annotations

import json
import os
import sys

# GF(q) for q in {2,3,4,5,7,8,9}: (p, k, modulus coefficients low->high)
_FIELDS = {2: (2, 1, None), 3: (3, 1, None), 5: (5, 1, None), 7: (7, 1, None),
           4: (2, 2, [1, 1, 1]), 8: (2, 3, [1, 1, 0, 1]), 9: (3, 2, [1, 0, 1])}


class GF:
    def __init__(self, q):
        self.q = q
        self.p, self.k, self.mod = _FIELDS[q]

    def digits(self, a):
        return [(a // self.p ** i) % self.p for i in range(self.k)]

    def num(self, d):
        return sum(x * self.p ** i for i, x in enumerate(d))

    def add(self, a, b):
        return self.num([(x + y) % self.p for x, y in zip(self.digits(a), self.digits(b))])

    def neg(self, a):
        return self.num([(-x) % self.p for x in self.digits(a)])

    def mul(self, a, b):
        if self.k == 1:
            return a * b % self.p
        da, db = self.digits(a), self.digits(b)
        prod = [0] * (2 * self.k - 1)
        for i, x in enumerate(da):
            for j, y in enumerate(db):
                prod[i + j] = (prod[i + j] + x * y) % self.p
        # reduce by monic modulus of degree k
        for deg in range(len(prod) - 1, self.k - 1, -1):
            c = prod[deg]
            if c:
                for i in range(self.k + 1):
                    prod[deg - self.k + i] = (prod[deg - self.k + i] - c * self.mod[i]) % self.p
        return self.num(prod[:self.k])


def field_design(M, K, balanced=True):
    """List of rounds; each round is M groups of K bowler ids (id = i*M + v),
    listed in pair order.  With balanced=True (and K < M) the group a of round
    x is put on pair a + c*x with c = field element K, so bowler (i, v) sits on
    pair v + (c - e_i) x: a different pair every round (lane-pair balance).
    For K = M no such c exists (and the extra 'same type' round is added only
    when balanced=False)."""
    if M not in _FIELDS or K > M:
        return None
    F = GF(M)
    c = K if (balanced and K < M) else 0
    rounds = []
    for x in range(M):
        blk = [None] * M
        for a in range(M):
            blk[F.add(a, F.mul(c, x))] = [i * M + F.add(a, F.mul(i, x)) for i in range(K)]
        rounds.append(blk)
    if K == M and not balanced:
        rounds.append([[i * M + v for v in range(M)] for i in range(K)])
    return rounds


def check(rounds):
    seen = set()
    for blk in rounds:
        for g in blk:
            for i in range(len(g)):
                for j in range(i + 1, len(g)):
                    c = (min(g[i], g[j]), max(g[i], g[j]))
                    if c in seen:
                        return False
                    seen.add(c)
    return True


if __name__ == "__main__":
    for M in (3, 4, 5, 7, 8, 9):
        for K in range(2, min(M, 5) + 1):
            d = field_design(M, K)
            from model import evaluate
            r = evaluate([[g for g in blk] for blk in d])
            print(M, K, len(d), "rounds", "ok" if check(d) else "REPEAT", "pair_spread", r["pair_spread"])
