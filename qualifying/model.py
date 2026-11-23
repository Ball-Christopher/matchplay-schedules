"""Qualifying lane-movement model and evaluator.

A *draw* is a list of blocks; each block is a list of M pairs; each pair is a
list of K bowler ids (0..M*K-1) in bowling order (position 1 first).

Bowling order position q (1-based) starts on the left lane if q is odd and on
the right lane if q is even.  American format: every bowler changes lane every
frame.  In frame f (0-based) the bowler in position q is on the left lane iff
(q - 1 + f) is even, and the bowlers on a lane bowl in bowling order.  So the
left lane sees odd positions (ascending) in frame 1, even positions in frame 2,
odd again in frame 3 ...; the right lane sees the same cycle half a turn out of
phase.  Both lanes therefore run through the single cyclic order

    LANE_CYCLE(K) = 1, 3, 5, ..., 2, 4, 6, ...     (odds then evens)

and a bowler always bowls immediately after the bowler before them in that
cycle ("follows" them), on both lanes, all block.

    K=2: 1 2        -> 2 follows 1 and 1 follows 2
    K=3: 1 3 2      -> 3 follows 1, 2 follows 3, 1 follows 2
    K=4: 1 3 2 4    -> 3 f 1, 2 f 3, 4 f 2, 1 f 4
    K=5: 1 3 5 2 4  -> 3 f 1, 5 f 3, 2 f 5, 4 f 2, 1 f 4
"""
from __future__ import annotations

from itertools import combinations

# pair_spread comes first: lane-pair balance is a hard constraint (every
# bowler on every pair floor/ceil(B/M) blocks), ahead of all mixing fields.
SCORE_FIELDS = ("pair_spread", "max_meet", "max_follow", "repeats", "follow_repeats",
                "max_ufollow", "ufollow_repeats", "neg_min_meet",
                "side_spread", "pos_spread")
MIXING_FIELDS = SCORE_FIELDS[1:8]


def lane_cycle(K):
    return list(range(1, K + 1, 2)) + list(range(2, K + 1, 2))


def predecessor(K):
    """pred[q] = position (1-based) that position q follows on the lane."""
    c = lane_cycle(K)
    return {c[i]: c[i - 1] for i in range(K)}


def evaluate(draw):
    """Score a draw.  Returns a dict of metrics; 'score' is the lexicographic
    tuple (smaller is better) in SCORE_FIELDS order."""
    B = len(draw)
    M = len(draw[0])
    K = len(draw[0][0])
    n = M * K
    pred = predecessor(K)
    meet = [[0] * n for _ in range(n)]
    follow = [[0] * n for _ in range(n)]  # follow[a][b]: a bowls right after b
    visits = [[0] * M for _ in range(n)]
    posc = [[0] * K for _ in range(n)]
    left = [0] * n
    for blk in draw:
        assert len(blk) == M
        seen = sorted(x for pr in blk for x in pr)
        assert seen == list(range(n)), "each bowler exactly once per block"
        for p, pr in enumerate(blk):
            assert len(pr) == K
            for a, b in combinations(pr, 2):
                meet[a][b] += 1
                meet[b][a] += 1
            for i, a in enumerate(pr):
                q = i + 1
                visits[a][p] += 1
                posc[a][i] += 1
                if q % 2 == 1:
                    left[a] += 1
                b = pr[pred[q] - 1]
                if b != a:
                    follow[a][b] += 1
    pairs = [meet[a][b] for a in range(n) for b in range(a + 1, n)]
    fol = [follow[a][b] for a in range(n) for b in range(n) if a != b]
    ufol = [follow[a][b] + follow[b][a] for a in range(n) for b in range(a + 1, n)]
    r = dict(M=M, K=K, B=B)
    r["max_meet"] = max(pairs)
    r["min_meet"] = min(pairs)
    r["repeats"] = sum(max(0, m - 1) for m in pairs)
    r["never_met"] = sum(1 for m in pairs if m == 0)
    r["max_follow"] = max(fol)
    r["follow_repeats"] = sum(max(0, f - 1) for f in fol)
    r["max_ufollow"] = max(ufol)
    r["ufollow_repeats"] = sum(max(0, f - 1) for f in ufol)
    # distinct bowlers each bowler follows / is followed by (min over bowlers)
    r["min_distinct_followed"] = min(sum(1 for b in range(n) if follow[a][b]) for a in range(n))
    r["min_distinct_followers"] = min(sum(1 for b in range(n) if follow[b][a]) for a in range(n))
    r["pair_spread"] = max(max(v) - min(v) for v in visits)
    r["side_spread"] = max(left) - min(left)
    r["pos_spread"] = max(max(c) - min(c) for c in posc)
    r["score"] = tuple(-r["min_meet"] if f == "neg_min_meet" else r[f]
                       for f in SCORE_FIELDS)
    return r


def rule_draw(M, K, B, d, pi):
    """Explicit draw of a movement rule.  Types are positions 0..K-1.
    After each block the bowler in (pair p, position t) moves to
    (pair p + d[t] mod M, position pi[t]).  Bowler id = p*K + t at block 1."""
    slot = {p * K + t: (p, t) for p in range(M) for t in range(K)}
    draw = []
    for _ in range(B):
        blk = [[None] * K for _ in range(M)]
        for a, (p, t) in slot.items():
            blk[p][t] = a
        draw.append(blk)
        slot = {a: ((p + d[t]) % M, pi[t]) for a, (p, t) in slot.items()}
    return draw


def rule_exclusion(M, K, d, pi):
    """Couples (unordered) that can never share a pair under the rule however
    many blocks are run, and ordered couples that can never follow.  The rule
    is periodic with period dividing M * order(pi), so that horizon suffices."""
    order, x = 1, list(pi)
    while x != list(range(K)):
        x = [pi[v] for v in x]
        order += 1
    horizon = M * order
    n = M * K
    draw = rule_draw(M, K, horizon, d, pi)
    pred = predecessor(K)
    met, fol = set(), set()
    for blk in draw:
        for pr in blk:
            for a, b in combinations(sorted(pr), 2):
                met.add((a, b))
            for i, a in enumerate(pr):
                b = pr[pred[i + 1] - 1]
                if a != b:
                    fol.add((a, b))
    return dict(never_meet=n * (n - 1) // 2 - len(met),
                never_follow=n * (n - 1) - len(fol), period=horizon)


def lower_bounds(M, K, B, sgp_max):
    """Simple lower bounds on (max_meet, repeats, neg_min_meet) for any draw.
    sgp_max: best known / proven max rounds with no repeat (social golfer)."""
    n = M * K
    per = (K - 1) * B                    # meetings per bowler (with multiplicity)
    mm = max(1, -(-per // (n - 1)))
    if B > sgp_max and mm == 1:
        mm = 2
    rep = (n * max(0, per - (n - 1)) + 1) // 2
    minm = per // (n - 1)
    return mm, rep, -minm


def describe_rule(M, K, d, pi):
    """Plain-words description: one line per starting position."""
    def side(t):
        return "left" if t % 2 == 0 else "right"

    def ordinal(t):
        return {1: "1st", 2: "2nd", 3: "3rd"}.get(t, f"{t}th")

    out = []
    for t in range(K):
        dd = d[t] % M
        if dd > M // 2 or (dd * 2 == M and False):
            dd -= M
        if dd == 0:
            mv = "stay on the pair"
        elif dd > 0:
            mv = f"move {dd} pair{'s' if dd > 1 else ''} right"
        else:
            mv = f"move {-dd} pair{'s' if dd < -1 else ''} left"
        if pi[t] == t:
            nxt = "keep position"
        else:
            nxt = f"bowl {ordinal(pi[t] + 1)} ({side(pi[t])} lane)"
        out.append(f"{ordinal(t + 1)} ({side(t)} lane): {mv}, {nxt}")
    return "; ".join(out)
