# League schedules for up to 40 bowlers

Results checked against [commit 33d41db](https://github.com/Ball-Christopher/matchplay-schedules/tree/33d41db). The status below covers the two requested qualifying objectives and the fixed-first-round versions of the two-round oil problem. Lower-priority tie-breakers such as the total number of repeats can distinguish draws with identical maxima.

## Two-round matchplay

The first half of each draw reproduces the published file, including lane pairs and bowling positions. Both halves and the combined schedule are lane- and position-balanced. A single value is proved optimal. Each interval runs from a proved lower bound to the number of patterns attained by the attached draw.

| Bowlers | Group size | Published oil round first | Published main round first |
|---:|---:|---:|---:|
| 24 | 3 | 5–6 | 18–19 |
| 24 | 4 | 8 | 16 |
| 30 | 3 | 5 | 18 |
| 32 | 4 | 8 | 8 |
| 36 | 3 | 5–6 | 24 |
| 36 | 4 | 14–15 | 29–30 |

At 32 in fours, the last eight-week block of either first round leaves just seven eligible quartets for an additional week. Eight are needed. At 24 in fours with the main file first, reaching 15 patterns would require two further clash-free weeks at the boundary. Exhaustive enumeration gives zero such continuations. These conclusions hold over all possible second-round designs.

## One-round matchplay

**36 in fours.** Four patterns are both sufficient and necessary. All 35 weekly partitions are distinct. The pattern lengths are 9 + 9 + 9 + 8. Each of the 630 couples meets three times and never twice on the same pattern. Every bowler visits each lane pair three or four times. At every season prefix the spread in couple meeting counts is at most two, and every player’s position counts differ by at most one.

**36 in trios.** An independently constructed three-pattern round has lengths 3 + 16 + 16. Every couple meets twice. The short three-week pattern consists of within-layer games. Each longer pattern combines four within-layer weeks with twelve transversal weeks. All lane and position counts are balanced.

## Qualifying draws

The table gives the maximum times any couple meets followed by the maximum times any ordered follower–predecessor pair occurs. All rows satisfy lane-pair balance. The commit column reports the maxima already achieved in the published draw. “Exact” refers to both maxima in lexicographic order.

| Lane pairs × bowlers | Blocks | Commit | Attached draw | Status |
|---|---:|---:|---:|---|
| 3 × 3 | 3 | (3, 2) | **(3, 2)** | Exact |
| 3 × 3 | 6 | (2, 2) | **(2, 1)** | Exact |
| 3 × 4 | 7 | (3, 1) | **(3, 1)** | Exact |
| 3 × 4 | 11 | (4, 2) | **(4, 2)** | Meetings exact, follows 1–2 |
| 3 × 5 | 12 | (4, 2) | **(4, 1)** | Exact |
| 4 × 3 | 6 | (2, 1) | **(2, 1)** | Exact |
| 4 × 3 | 9 | (2, 2) | **(2, 1)** | Exact |
| 4 × 3 | 10 | (2, 2) | **(2, 1)** | Exact |
| 4 × 3 | 11 | (2, 2) | **(2, 1)** | Exact |
| 4 × 4 | 9 | (3, 1) | **(2, 1)** | Exact |
| 4 × 4 | 10 | (3, 1) | **(2, 1)** | Exact |
| 5 × 3 | 7 | (2, 1) | **(2, 1)** | Exact |
| 5 × 3 | 11 | (2, 2) | **(2, 1)** | Exact |
| 5 × 3 | 12 | (2, 2) | **(2, 1)** | Exact |
| 6 × 3 | 7 | (2, 1) | **(1, 1)** | Exact |
| 6 × 3 | 8 | (2, 1) | **(1, 1)** | Exact |
| 6 × 3 | 12 | (2, 2) | **(2, 1)** | Exact |
| 6 × 4 | 6 | (2, 1) | **(2, 1)** | Exact |
| 6 × 5 | 4 | (2, 1) | **(2, 1)** | Exact |
| 6 × 5 | 5 | (2, 1) | **(2, 1)** | Exact |
| 6 × 5 | 6 | (2, 1) | **(2, 1)** | Exact |
| 7 × 3 | 10 | (2, 1) | **(1, 1)** | Exact |
| 7 × 4 | 8 | (2, 1) | **(1, 1)** | Exact |
| 7 × 4 | 9 | (2, 1) | **(1, 1)** | Exact |
| 7 × 5 | 11 | (2, 2) | **(2, 1)** | Exact |
| 7 × 5 | 12 | (2, 2) | **(2, 1)** | Exact |
| 8 × 3 | 10 | (2, 1) | **(1, 1)** | Exact |
| 8 × 3 | 11 | (2, 1) | **(1, 1)** | Exact |
| 8 × 4 | 9 | (2, 1) | **(1, 1)** | Exact |
| 9 × 3 | 10 | (2, 1) | **(1, 1)** | Exact |
| 9 × 3 | 11 | (2, 1) | **(1, 1)** | Exact |
| 9 × 3 | 12 | (2, 1) | **(1, 1)** | Exact |
| 10 × 4 | 12 | (2, 1) | **(1, 1)** | Exact |

33 attached qualifying draws. 24 improve the published maximum meeting or follow count. For the other rows the published draw supplies a witness and the new argument certifies the indicated bound.

## Open within this scope

The 24-bowler fours spread-one question, the six-block 5×3 qualifying question, the intervals in the two-round table and other qualifying cases outside this table remain open in this study. Problems 1 and 5 were already settled in the source. The updated commit includes the rotating vacancies.

## Reproducibility

The archive includes the three schedule tables, per-draw JSON, methods and unsuccessful approaches. From its extracted directory run `python verify_results.py` to recount every couple, lane and position in matchplay and every meeting and directed follow in qualifying. Pass a checkout of 33d41db as an argument to compare the first-round weekly rows directly. Run `python proofs/check_boundary.py` and `python proofs/check_kirkman.py` for the two finite exclusion checks.
