"""Score common lane-movement schemes (stage 1 baseline).

    python3 baselines.py      -> results/baselines.json

Schemes, all written as movement rules (d, pi) on positions 0..K-1
(position t starts on the left lane iff t is even):

  nz      "Left lane moves one pair left, right lane one pair right"
          (current NZ practice; the IESA state finals sheet: "odd lanes move
          left ... even lanes move right" within the block, wrapping round; the
          CDE scoring software's "Even to Right --> <-- Odd to Left").
  pairs   "Move pairs to the right": every bowler moves one pair right
          together (CDE "Move pairs to the Right"); company never changes.
  lane    "Single lane right": every lane's bowlers move one lane right, so a
          left-lane group becomes the right-lane group of the same pair and a
          right-lane group becomes the left-lane group of the next pair
          (CDE "Single lane Right"); even K only.
  nz_line the NZ rule on pairs in a line WITHOUT wrap-around: bowlers who
          would step off an end cross to the other lane of the end pair and
          reverse direction (even K only; see nz_line_draw).
"""
from __future__ import annotations

import json
import os

from model import evaluate, rule_draw, rule_exclusion

HERE = os.path.dirname(os.path.abspath(__file__))


def schemes(M, K):
    out = {}
    out["nz"] = ([-1 if t % 2 == 0 else 1 for t in range(K)], list(range(K)))
    out["pairs"] = ([1] * K, list(range(K)))
    if K % 2 == 0:
        d = [0 if t % 2 == 0 else 1 for t in range(K)]
        pi = [t + 1 if t % 2 == 0 else t - 1 for t in range(K)]
        out["lane"] = (d, pi)
    return out


def nz_line_draw(M, K, B):
    """NZ rule with pairs in a line and no wrap-around (K even): at the ends
    the bowlers who would leave the block cross to the other lane of the end
    pair and change direction.  In 'unfolded' coordinates u in Z_2M (u < M:
    right lane of pair u moving right; u >= M: left lane of pair 2M-1-u moving
    left) every bowler simply does u -> u + 1."""
    assert K % 2 == 0
    st = {}
    for p in range(M):
        for t in range(K):
            j = t // 2
            u = (2 * M - 1 - p) if t % 2 == 0 else p
            st[p * K + t] = (u, j)
    draw = []
    for _ in range(B):
        blk = [[None] * K for _ in range(M)]
        for a, (u, j) in st.items():
            if u < M:
                blk[u][2 * j + 1] = a
            else:
                blk[2 * M - 1 - u][2 * j] = a
        draw.append(blk)
        st = {a: ((u + 1) % (2 * M), j) for a, (u, j) in st.items()}
    return draw


def main():
    res = []
    for K in (2, 3, 4, 5):
        for M in range(3, 11):
            for name, (d, pi) in schemes(M, K).items():
                ex = rule_exclusion(M, K, d, pi)
                for B in range(1, 13):
                    r = evaluate(rule_draw(M, K, B, d, pi))
                    res.append(dict(scheme=name, M=M, K=K, B=B, d=[x % M for x in d], pi=pi,
                                    score=list(r["score"]), never_meet_ever=ex["never_meet"],
                                    never_follow_ever=ex["never_follow"],
                                    min_distinct_followed=r["min_distinct_followed"],
                                    never_met=r["never_met"]))
            if K % 2 == 0:
                for B in range(1, 13):
                    r = evaluate(nz_line_draw(M, K, B))
                    res.append(dict(scheme="nz_line", M=M, K=K, B=B, d=None, pi=None,
                                    score=list(r["score"]), never_meet_ever=None,
                                    never_follow_ever=None,
                                    min_distinct_followed=r["min_distinct_followed"],
                                    never_met=r["never_met"]))
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(res, open(os.path.join(HERE, "results", "baselines.json"), "w"))
    print(len(res), "rows")


if __name__ == "__main__":
    main()
