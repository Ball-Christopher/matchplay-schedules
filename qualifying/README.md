# Qualifying lane movements

Who bowls with whom, who follows whom, and on which pair, in a qualifying
squad where bowlers move between blocks of games. Everything here can be
regenerated from the code in this folder (see [Reproducing](#reproducing)).

## The problem

A squad of **M pairs** (3–10) with **K bowlers per pair** (2–5) bowls N games
in blocks of g games; bowlers move pair between blocks, so there are
**B = ⌈N/g⌉ blocks** (1–12). Only the blocks matter for mixing, so all results
are by B. With g = 2 (usual in NZ), B = 3, 4, 5, 6 means N = 5–6, 7–8, 9–10,
11–12 games; with g = 1, N = B.

### Bowling order and the follow relation

On a pair the bowlers are in bowling order 1..K and start alternately on the
left and right lane (1 left, 2 right, 3 left, ...). In American format every
bowler changes lane every frame, so in frame f the bowler in position q is on
the left lane when q − 1 + f is even. Each lane therefore sees the odd
positions (in order) in one frame and the even positions the next. Both
lanes run through the same cycle, half a turn apart:

    lane cycle = 1, 3, 5, …, 2, 4, 6, …   (odd positions, then even positions)

A bowler always bowls immediately after the bowler before them in this cycle
("follows" them), on both lanes, every frame, for the whole block:

| K | lane cycle | who follows whom |
|---|---|---|
| 2 | 1 2 | 2 follows 1 and 1 follows 2 |
| 3 | 1 3 2 | 3 follows 1, 2 follows 3, 1 follows 2 |
| 4 | 1 3 2 4 | 3 follows 1, 2 follows 3, 4 follows 2, 1 follows 4 |
| 5 | 1 3 5 2 4 | 3 f 1, 5 f 3, 2 f 5, 4 f 2, 1 f 4 |

So with K = 4 the two bowlers who start on the left lane (1st and 3rd) are
always consecutive on the lane: 3rd follows 1st. For K = 2 the two bowlers
follow each other both ways, so following is the same as pairing. For odd K
the cycle still has length K (for K = 3, 1st follows 2nd: the left lane sees
1, 3 | 2 | 1, 3 | …).

### Movement rules

A **movement rule** gives every seat the same instruction each block, the same
on every pair: the bowler in (pair p, position t) moves to
(pair p + d_t mod M, position π(t)). Pairs are in a line, but movement
**wraps round**: moving left from pair 1 goes to pair M. Real centres do this.
The Illinois (IESA) state-finals sheet, for example, moves a bowler from lane 3
"left" to lane 13 at the other end of the block. Wrap-around only matters for
saying a rule as "move d pairs". An explicit draw table can use any order of
pairs. See [Without wrap-around](#without-wrap-around) for what happens
without it.

## Scoring

Every scheme is scored from its explicit draw (`model.evaluate`). The score is
lexicographic: earlier fields matter more, and smaller is better.

| # | field | meaning |
|---|---|---|
| 0 | `pair_spread` | **Hard constraint: lane-pair balance.** For each bowler, the most blocks on one pair minus the fewest. It must be at its minimum (0 if M divides B, else 1). That means every bowler bowls every pair ⌊B/M⌋ or ⌈B/M⌉ blocks, and so never repeats a pair while B ≤ M. Only schemes that meet this are recommended. |
| 1 | `max_meet` | most blocks any couple shares a pair |
| 2 | `max_follow` | most blocks any ordered (follower, followed) couple occurs |
| 3 | `repeats` | Σ over couples of (meetings − 1)⁺ (repeated meetings) |
| 4 | `follow_repeats` | Σ over ordered couples of (follows − 1)⁺ |
| 5 | `max_ufollow` | most blocks either of a couple follows the other (unordered) |
| 6 | `ufollow_repeats` | Σ (unordered follows − 1)⁺ |
| 7 | `neg_min_meet` | −(fewest meetings of any couple). For large B this rewards everyone meeting everyone (all counts within 1). |
| 8 | `side_spread` | spread across bowlers of blocks started on the left lane |
| 9 | `pos_spread` | for each bowler, most blocks in one bowling position minus the fewest |

Simplicity (a rule rather than a table) only breaks ties. Among rules, the
search also prefers fewer **structurally excluded couples**: couples who can
never share a pair however long the rule runs.

Why this order: the organiser's brief is "no advantage from the pair you bowl
on" first. After that comes "not with, or behind, the same person". Following
is scored as an ordered pair (being behind the same person every frame is the
actual grievance) and comes before total repeats. Wherever a design has no
repeated meetings, no follow can repeat either, since following needs a
meeting. Side balance matters little with g = 2. With the usual alternation
(game 2 of a block starts on the other lane), every two-game block already
gives one left start and one right start. It matters for g = 1 and for a short
last block. Position balance matters mostly for 1st (warm lane, no wait) versus
last.

Short last block (odd N with g = 2): when B ≤ M every bowler has distinct
pairs, so per-pair game counts are 2 or 1 or 0, as even as the block structure
allows. The 1-game block can be put on any pair without breaking balance. For
B > M the block-level balance leaves at most one extra game on a pair.

### Lower bounds used for "proven optimal"

* Pairings: each bowler meets (K−1)B others (with repeats) out of MK−1. That
  gives `max_meet` ≥ ⌈(K−1)B/(MK−1)⌉ and a floor on repeats. Zero repeats needs
  a **social golfer** solution with M groups of K for B rounds. The bound is
  B ≤ (MK−1)/(K−1). If M < K, only one round is possible, because a group in
  round 2 would need K bowlers from different round-1 pairs. Known and proven
  maxima come from Miller, Valkov & Abel, *Combinatorial solutions to the Social
  Golfer Problem…*, [arXiv:2507.23376](https://arxiv.org/abs/2507.23376),
  Tables B4–B7 (Warwick Harvey's results page is the older source).
* Following (K ≥ 3): each bowler follows B bowlers out of MK−1, so
  `max_follow` ≥ ⌈B/(MK−1)⌉.
* Pair, side and position spreads: 0 if the average is a whole number, else 1.

A scheme is **proven optimal** on a field when it reaches these bounds on that
field and on every earlier one. Lane-pair balance can push mixing above the
simple bounds (see below). In those cases the bound is not tight and "?" only
means "not proven".

## Structural facts

1. **Any movement rule excludes M − 1 partners per bowler.** Two bowlers who
   start in the same position on different pairs follow the same path,
   shifted, so they never meet, whatever π is. So each bowler can meet at most
   (K−1)M of the MK−1 others, and a rule can never get everyone to meet
   (`min_meet` = 0). Under a rule, a couple of starting positions (t, u) has
   only M possible offsets. So zero repeats is impossible once B > M, and
   `max_meet` ≥ ⌈B/M⌉. Unrestricted draws can reach the social-golfer bound,
   which can be up to (MK−1)/(K−1) ≈ M·K/(K−1).
2. **π = identity** (everyone keeps their position): positions t, u meet at
   pair offset b(d_t − d_u) in block b. B ≤ M blocks without repeats needs
   every difference d_t − d_u to be a unit mod M. Lane-pair balance also needs
   every d_t to be a unit, or else that bowler comes back to a pair. So
   {0, d_1, …, d_K} must have pairwise unit differences, which is possible iff
   **K + 1 ≤ p(M)**, the smallest prime factor of M. Under balance, such
   rules give perfect mixing for B ≤ M when M = 5 and K ≤ 4, M = 7 and K ≤ 5
   (in fact K ≤ 6), and M = 3, 5, 7, 9 when K = 2. They cannot when M is even
   and K ≥ 2 (K = 2 with even M repeats at block M/2 + 1), nor when M = 9 and
   K ≥ 3. A bowler in position t then always follows a position-pred(t) bowler
   (a different one each block) and always starts on the same side.
3. **Type-permuting rules** (π ≠ id, e.g. bowling order rotates) help a little
   for composite M. They also balance sides and positions, but they exclude
   *more* couples structurally. With lane-pair balance, the best rule has no
   repeats for this many blocks:

   | | M=3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
   |---|---|---|---|---|---|---|---|---|
   | K=2 | 3 | 2 | 5 | 3 | 7 | 4 | 9 | 5 |
   | K=3 | 1 | 2 | 5 | 3 | 7 | 4 | 3 | 5 |
   | K=4 | 1 | 1 | 5 | 3 | 7 | 4 | 4 | 5 |
   | K=5 | 1 | 1 | 1 | 2 | 7 | 5 | 5 | 5 |

4. **Lane-pair balance is not free for unrestricted draws either.** When
   M ≤ K, even 2 blocks force a repeat. A block-2 group on pair q may not
   contain anyone from block 1's group on pair q, so its K bowlers come from
   only M − 1 block-1 groups, and two of them must have met already. z3
   (`exact.py`, exact model with balance) proves the least possible
   `max_meet` under balance for the small cases: **3×3: B=2 → 2, B=3 → 3**
   (some couple shares all three blocks); **3×4 B=3 → 3**; 3×5 B=3, 4 → 3;
   4×4, 5×5, 4×5 B=2–6 → 2; 6×4 B=5 and 6×3 B=6 → 1 (found by z3, not by the
   anneal). Without balance, the affine planes give 1 for 3×3 B≤4, 4×4 B≤5 and
   5×5 B≤6. The full list is under "Where lane-pair balance forces worse
   mixing" below. Differences of 1 in the repeat counts at large B there are
   probably search noise, not real costs.

## The NZ rule (and other common rules), in plain words

The NZ rule: left-lane bowlers move one pair left, right-lane bowlers one pair
right, and everyone keeps their position. The CDE scoring software calls this
"Even to Right <-- Odd to Left". The IESA sheet says "odd lanes move left,
even lanes move right".

* **K ≥ 3:** all bowlers who start on the same lane of a pair move together for
  the whole session. With K = 4, the 1st and 3rd stay together every block, and
  3rd **follows** 1st on every frame of every game. The same goes for 2nd and
  4th. With K = 5, positions 1, 3 and 5 stay together all session. So
  `max_meet` = `max_follow` = B whatever M is.
* **Who can ever meet** (structural exclusion): a left-lane bowler only ever
  meets their lane-mate(s) and right-lane bowlers who started an *even* number
  of pairs away. They never meet another left-lane starter, and when M is even
  they never meet half the right-lane starters either.
* **K = 2:** fine for odd M (no repeats for B ≤ M). For even M, couples
  meet again after M/2 blocks (M = 4: at block 3; M = 6: at block 4).

Worked example, M = 4, K = 4, NZ rule (bowlers A–P, positions in order;
block 1 = ABCD on pair 1):

| block | pair 1 | pair 2 | pair 3 | pair 4 |
|---|---|---|---|---|
| 1 | ABCD | EFGH | IJKL | MNOP |
| 2 | ENGP | IBKD | MFOH | AJCL |
| 3 | IJKL | MNOP | ABCD | EFGH |
| 4 | MFOH | AJCL | ENGP | IBKD |

A and C are together in every block (C follows A on every frame). The
original foursomes are back together in block 3. Over any number of blocks
A only ever meets B, C, D, J and L, which is 5 of the 15 others.

The other common schemes are worse for mixing:

* "Move pairs" (all bowlers move together, CDE "Move pairs to the Right"):
  the company never changes, so `max_meet` = `max_follow` = B.
* "Single lane right" (every lane's bowlers move one lane right): a group of
  lane-mates is never split, and each bowler repeats a pair in consecutive
  blocks. That breaks lane-pair balance.

### Without wrap-around

If the pairs are a line with no wrap, a bowler who would step off an end has
to stay on the end pair. In practice they cross to its other lane and reverse
direction. Either way, they bowl the end pair two blocks running, so lane-pair
balance fails as soon as anyone reaches an end (`nz_line` in
`results/baselines.json`: `pair_spread` = 2 from B = 2 or 3). On a line, a rule
of the form "move d pairs" cannot keep every bowler on distinct pairs. A
centre that does not want bowlers walking from one end of the block to the
other must use an explicit draw table. A draw can put the pairs in any order,
but a bowler will still sometimes have to cross the block.

## Results

Legend for the first table: **R** = a movement rule achieves it; **r** = a
rule matches the best on the mixing fields, but an explicit draw has better
side or position balance (the draw is recommended); **D** = an explicit draw is
needed; **?** = max meetings or max follows not proven optimal (bounds:
counting, social golfer, z3). All entries are lane-pair balanced.

### Main findings

* **Perfect mixing** means everyone on distinct pairs, nobody shares a pair
  twice and nobody follows the same person twice. It is achieved for
  B ≤ min(M, SGP horizon) in almost every case with M > K. Rules give it for
  B ≤ M when K + 1 ≤ smallest prime factor of M (M = 5, 7, and 9 for K = 2).
  Explicit draws extend it, e.g. 4×3 B≤4, 6×3 B≤6, 6×4 B≤5, 8×4 B≤8, 9×4 B≤9,
  8×5 B≤8, 9×5 B≤9 (see the zero-repeat table).
* **The NZ rule** is perfect only for K = 2 with odd M (and for B ≤ M/2 with
  even M). For every K ≥ 3 the same-lane bowlers are together all session, so
  `max_meet` = `max_follow` = B. For 6 pairs of 4 bowling 12 games, that is 6/6
  with 132 repeated meetings, against 2/1 with 17 for the best balanced draw
  (and 1/1/0 up to 10 games).
* **Following** is never the binding problem in good designs: `max_follow` = 1
  wherever couples meet at most once. Once repeats are forced, ordered follows
  can still almost always be kept at 1.
* **Structural exclusion**: every rule leaves M − 1 partners per bowler
  unreachable (same starting position), and the NZ rule leaves many more. The
  explicit draws have no structural exclusion. For B large enough
  (B(K−1) ≥ MK−1) they can be found with everyone meeting (`min_meet` ≥ 1),
  which no rule can do.

### Best achievable mixing (max meetings / max ordered follows per couple)

| M×K | B=1 | B=2 | B=3 | B=4 | B=5 | B=6 | B=7 | B=8 | B=9 | B=10 | B=11 | B=12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3×2 | 1/1 R | 1/1 r | 1/1 r | 1/1 D | 1/1 D | 2/2 D | 2/2 D | 2/2 D | 2/2 D | 2/2 D | 3/3 D | 3/3 D |
| 4×2 | 1/1 R | 1/1 r | 1/1 D | 1/1 D | 1/1 D | 1/1 D | 1/1 D | 2/2 D | 2/2 D | 2/2 D | 2/2 D | 2/2 D |
| 5×2 | 1/1 R | 1/1 r | 1/1 r | 1/1 r | 1/1 r | 1/1 D | 1/1 D | 1/1 D | 1/1 D | 2/2 D | 2/2 D | 2/2 D |
| 6×2 | 1/1 R | 1/1 r | 1/1 r | 1/1 D | 1/1 D | 1/1 D | 1/1 D | 1/1 D | 1/1 D | 1/1 D | 1/1 D | 2/2 D |
| 7×2 | 1/1 R | 1/1 r | 1/1 r | 1/1 r | 1/1 r | 1/1 r | 1/1 r | 1/1 D | 1/1 D | 1/1 D | 1/1 D | 1/1 D |
| 8×2 | 1/1 R | 1/1 r | 1/1 r | 1/1 r | 1/1 D | 1/1 D | 1/1 D | 1/1 D | 1/1 D | 1/1 D | 1/1 D | 1/1 D |
| 9×2 | 1/1 R | 1/1 r | 1/1 r | 1/1 r | 1/1 r | 1/1 r | 1/1 r | 1/1 r | 1/1 r | 1/1 D | 1/1 D | 1/1 D |
| 10×2 | 1/1 R | 1/1 r | 1/1 r | 1/1 r | 1/1 r | 1/1 D | 1/1 D | 1/1 D | 1/1 D | 1/1 D | 1/1 D | 1/1 D |
| 3×3 | 1/1 R | 2/1 R | 3/2 r? | 2/1 D | 2/1 D | 2/2 D? | 2/1 D | 2/1 D | 3/2 D | 3/2 D | 3/2 D | 3/2 D |
| 4×3 | 1/1 R | 1/1 r | 1/1 D | 1/1 D | 2/1 D | 2/1 D | 2/1 D | 2/1 D | 2/2 D? | 2/2 D? | 2/2 D? | 3/2 D |
| 5×3 | 1/1 R | 1/1 r | 1/1 r | 1/1 r | 1/1 r | 2/1 D? | 2/1 D? | 2/1 D | 2/1 D | 2/1 D | 2/2 D? | 2/2 D? |
| 6×3 | 1/1 R | 1/1 r | 1/1 R | 1/1 D | 1/1 D | 1/1 D | 2/1 D? | 2/1 D? | 2/1 D | 2/1 D | 2/1 D | 2/2 D? |
| 7×3 | 1/1 R | 1/1 r | 1/1 r | 1/1 r | 1/1 r | 1/1 r | 1/1 r | 2/1 D? | 1/1 D | 2/1 D? | 2/1 D | 2/1 D |
| 8×3 | 1/1 R | 1/1 r | 1/1 r | 1/1 r | 1/1 D | 1/1 D | 1/1 D | 1/1 D | 2/1 D? | 2/1 D? | 2/1 D? | 2/1 D |
| 9×3 | 1/1 R | 1/1 r | 1/1 r | 1/1 D | 1/1 D | 1/1 D | 1/1 D | 1/1 D | 1/1 D | 2/1 D? | 2/1 D? | 2/1 D? |
| 10×3 | 1/1 R | 1/1 r | 1/1 r | 1/1 r | 1/1 r | 1/1 D | 1/1 D | 1/1 D | 2/1 D? | 2/1 D? | 2/1 D? | 2/1 D? |
| 3×4 | 1/1 R | 2/1 r | 3/1 r | 2/1 D | 2/1 D | 2/1 D | 3/1 D? | 3/1 D | 3/1 D | 3/2 D? | 4/2 D? | 4/2 D |
| 4×4 | 1/1 R | 2/1 r | 2/1 D | 2/1 D | 2/1 D | 2/1 D | 2/1 D | 2/1 D | 3/1 D? | 3/1 D? | 3/1 D | 3/1 D |
| 5×4 | 1/1 R | 1/1 r | 1/1 r | 1/1 r | 1/1 r | 2/1 D | 2/1 D | 2/1 D | 2/1 D | 2/1 D | 3/1 D? | 3/1 D? |
| 6×4 | 1/1 R | 1/1 r | 1/1 R | 1/1 D | 1/1 D | 2/1 D? | 2/1 D? | 2/1 D | 2/1 D | 2/1 D | 2/1 D | 3/1 D? |
| 7×4 | 1/1 R | 1/1 r | 1/1 r | 1/1 r | 1/1 r | 1/1 r | 1/1 r | 2/1 D? | 2/1 D? | 2/1 D | 2/1 D | 2/1 D |
| 8×4 | 1/1 R | 1/1 r | 1/1 r | 1/1 R | 1/1 D | 1/1 D | 1/1 D | 1/1 D | 2/1 D? | 2/1 D? | 2/1 D | 2/1 D |
| 9×4 | 1/1 R | 1/1 r | 1/1 r | 1/1 R | 1/1 D | 1/1 D | 1/1 D | 1/1 D | 1/1 D | 2/1 D? | 2/1 D? | 2/1 D |
| 10×4 | 1/1 R | 1/1 r | 1/1 r | 1/1 r | 1/1 r | 1/1 D | 1/1 D | 2/1 D? | 2/1 D? | 2/1 D? | 2/1 D? | 2/1 D? |
| 3×5 | 1/1 R | 2/1 r | 3/1 r | 3/1 D | 2/1 R | 2/1 D | 3/1 D | 3/1 D | 3/1 D | 4/1 D? | 4/1 D | 4/2 D? |
| 4×5 | 1/1 R | 2/1 r | 2/1 r | 2/1 r | 2/1 D | 2/1 D | 3/1 D? | 3/1 D? | 3/1 D? | 3/1 D | 3/1 D | 4/1 D? |
| 5×5 | 1/1 R | 2/1 r | 2/1 r | 2/1 D | 2/1 D | 2/1 D | 2/1 D | 2/1 D | 3/1 D? | 3/1 D? | 3/1 D? | 3/1 D? |
| 6×5 | 1/1 R | 1/1 r | 1/1 D | 2/1 D? | 2/1 D? | 2/1 D? | 2/1 D? | 2/1 D | 2/1 D | 2/1 D | 3/1 D? | 3/1 D? |
| 7×5 | 1/1 R | 1/1 r | 1/1 r | 1/1 r | 1/1 r | 1/1 r | 1/1 r | 2/1 D? | 2/1 D | 2/1 D | 2/2 R? | 2/2 R? |
| 8×5 | 1/1 R | 1/1 r | 1/1 r | 1/1 r | 1/1 R | 1/1 D | 1/1 D | 1/1 D | 2/1 D? | 2/1 D | 2/1 D | 2/1 D |
| 9×5 | 1/1 R | 1/1 r | 1/1 r | 1/1 r | 1/1 R | 1/1 D | 1/1 D | 1/1 D | 1/1 D | 2/1 D? | 2/1 D? | 2/1 D |
| 10×5 | 1/1 R | 1/1 r | 1/1 r | 1/1 r | 1/1 R | 1/1 D | 2/1 D? | 2/1 D? | 2/1 D? | 2/1 D? | 2/1 D? | 2/1 D? |

### Zero-repeat horizon: largest B with nobody sharing a pair twice

| M×K | NZ rule | best rule | any draw (found) | social-golfer max (known / proven) |
|---|---|---|---|---|
| 3×2 | 3 | 3 | 5 | 5 / 5 |
| 4×2 | 2 | 2 | 7 | 7 / 7 |
| 5×2 | 5 | 5 | 9 | 9 / 9 |
| 6×2 | 3 | 3 | 11 | 11 / 11 |
| 7×2 | 7 | 7 | 12 | 13 / 13 |
| 8×2 | 4 | 4 | 12 | 15 / 15 |
| 9×2 | 9 | 9 | 12 | 17 / 17 |
| 10×2 | 5 | 5 | 12 | 19 / 19 |
| 3×3 | 1 | 1 | 1 | 4 / 4 |
| 4×3 | 1 | 2 | 4 | 4 / 4 |
| 5×3 | 1 | 5 | 5 | 7 / 7 |
| 6×3 | 1 | 3 | 6 | 8 / 8 |
| 7×3 | 1 | 7 | 9 | 10 / 10 |
| 8×3 | 1 | 4 | 8 | 11 / 11 |
| 9×3 | 1 | 3 | 9 | 13 / 13 |
| 10×3 | 1 | 5 | 8 | 14 / 14 |
| 3×4 | 1 | 1 | 1 | 1 / 1 |
| 4×4 | 1 | 1 | 1 | 5 / 5 |
| 5×4 | 1 | 5 | 5 | 5 / 5 |
| 6×4 | 1 | 3 | 5 | 7 / 7 |
| 7×4 | 1 | 7 | 7 | 9 / 9 |
| 8×4 | 1 | 4 | 8 | 10 / 10 |
| 9×4 | 1 | 4 | 9 | 11 / 11 |
| 10×4 | 1 | 5 | 7 | 13 / 13 |
| 3×5 | 1 | 1 | 1 | 1 / 1 |
| 4×5 | 1 | 1 | 1 | 1 / 1 |
| 5×5 | 1 | 1 | 1 | 6 / 6 |
| 6×5 | 1 | 2 | 3 | 6 / 7 |
| 7×5 | 1 | 7 | 7 | 7 / 8 |
| 8×5 | 1 | 5 | 8 | 8 / 9 |
| 9×5 | 1 | 5 | 9 | 9 / 11 |
| 10×5 | 1 | 5 | 6 | 9 / 12 |

### NZ rule versus best, g=2 (B = 3, 4, 5, 6 ⇒ N = 6, 8, 10, 12 games)

Cells: max meetings / max ordered follows / repeated meetings (couple-blocks beyond the first).

| M×K | NZ B=3 | best B=3 | NZ B=4 | best B=4 | NZ B=5 | best B=5 | NZ B=6 | best B=6 |
|---|---|---|---|---|---|---|---|---|
| 3×2 | 1/1/0 | 1/1/0 | 2/2/3 | 1/1/0 | 2/2/6 | 1/1/0 | 2/2/9 | 2/2/3 |
| 4×2 | 2/2/4 | 1/1/0 | 2/2/8 | 1/1/0 | 3/3/12 | 1/1/0 | 3/3/16 | 1/1/0 |
| 5×2 | 1/1/0 | 1/1/0 | 1/1/0 | 1/1/0 | 1/1/0 | 1/1/0 | 2/2/5 | 1/1/0 |
| 6×2 | 1/1/0 | 1/1/0 | 2/2/6 | 1/1/0 | 2/2/12 | 1/1/0 | 2/2/18 | 1/1/0 |
| 7×2 | 1/1/0 | 1/1/0 | 1/1/0 | 1/1/0 | 1/1/0 | 1/1/0 | 1/1/0 | 1/1/0 |
| 8×2 | 1/1/0 | 1/1/0 | 1/1/0 | 1/1/0 | 2/2/8 | 1/1/0 | 2/2/16 | 1/1/0 |
| 9×2 | 1/1/0 | 1/1/0 | 1/1/0 | 1/1/0 | 1/1/0 | 1/1/0 | 1/1/0 | 1/1/0 |
| 10×2 | 1/1/0 | 1/1/0 | 1/1/0 | 1/1/0 | 1/1/0 | 1/1/0 | 2/2/10 | 1/1/0 |
| 3×3 | 3/3/6 | 3/2/6 | 4/4/15 | 2/1/9 | 5/5/24 | 2/1/12 | 6/6/33 | 2/2/18 |
| 4×3 | 3/3/16 | 1/1/0 | 4/4/28 | 1/1/0 | 5/5/40 | 2/1/3 | 6/6/52 | 2/1/7 |
| 5×3 | 3/3/10 | 1/1/0 | 4/4/15 | 1/1/0 | 5/5/20 | 1/1/0 | 6/6/35 | 2/1/1 |
| 6×3 | 3/3/12 | 1/1/0 | 4/4/30 | 1/1/0 | 5/5/48 | 1/1/0 | 6/6/66 | 1/1/0 |
| 7×3 | 3/3/14 | 1/1/0 | 4/4/21 | 1/1/0 | 5/5/28 | 1/1/0 | 6/6/35 | 1/1/0 |
| 8×3 | 3/3/16 | 1/1/0 | 4/4/24 | 1/1/0 | 5/5/48 | 1/1/0 | 6/6/72 | 1/1/0 |
| 9×3 | 3/3/18 | 1/1/0 | 4/4/27 | 1/1/0 | 5/5/36 | 1/1/0 | 6/6/45 | 1/1/0 |
| 10×3 | 3/3/20 | 1/1/0 | 4/4/30 | 1/1/0 | 5/5/40 | 1/1/0 | 6/6/70 | 1/1/0 |
| 3×4 | 3/3/12 | 3/1/12 | 4/4/30 | 2/1/24 | 5/5/48 | 2/1/36 | 6/6/66 | 2/1/54 |
| 4×4 | 3/3/32 | 2/1/12 | 4/4/56 | 2/1/24 | 5/5/80 | 2/1/24 | 6/6/104 | 2/1/29 |
| 5×4 | 3/3/20 | 1/1/0 | 4/4/30 | 1/1/0 | 5/5/40 | 1/1/0 | 6/6/70 | 2/1/6 |
| 6×4 | 3/3/24 | 1/1/0 | 4/4/60 | 1/1/0 | 5/5/96 | 1/1/0 | 6/6/132 | 2/1/17 |
| 7×4 | 3/3/28 | 1/1/0 | 4/4/42 | 1/1/0 | 5/5/56 | 1/1/0 | 6/6/70 | 1/1/0 |
| 8×4 | 3/3/32 | 1/1/0 | 4/4/48 | 1/1/0 | 5/5/96 | 1/1/0 | 6/6/144 | 1/1/0 |
| 9×4 | 3/3/36 | 1/1/0 | 4/4/54 | 1/1/0 | 5/5/72 | 1/1/0 | 6/6/90 | 1/1/0 |
| 10×4 | 3/3/40 | 1/1/0 | 4/4/60 | 1/1/0 | 5/5/80 | 1/1/0 | 6/6/140 | 1/1/0 |
| 3×5 | 3/3/24 | 3/1/24 | 4/4/54 | 3/1/34 | 5/5/84 | 2/1/60 | 6/6/114 | 2/1/90 |
| 4×5 | 3/3/56 | 2/1/24 | 4/4/96 | 2/1/48 | 5/5/136 | 2/1/60 | 6/6/176 | 2/1/80 |
| 5×5 | 3/3/40 | 2/1/15 | 4/4/60 | 2/1/30 | 5/5/80 | 2/1/89 | 6/6/130 | 2/1/52 |
| 6×5 | 3/3/48 | 1/1/0 | 4/4/108 | 2/1/6 | 5/5/168 | 2/1/22 | 6/6/228 | 2/1/41 |
| 7×5 | 3/3/56 | 1/1/0 | 4/4/84 | 1/1/0 | 5/5/112 | 1/1/0 | 6/6/140 | 1/1/0 |
| 8×5 | 3/3/64 | 1/1/0 | 4/4/96 | 1/1/0 | 5/5/176 | 1/1/0 | 6/6/256 | 1/1/0 |
| 9×5 | 3/3/72 | 1/1/0 | 4/4/108 | 1/1/0 | 5/5/144 | 1/1/0 | 6/6/180 | 1/1/0 |
| 10×5 | 3/3/80 | 1/1/0 | 4/4/120 | 1/1/0 | 5/5/160 | 1/1/0 | 6/6/260 | 1/1/0 |

### Recommended for g = 2 (B = 3..6), K = 2, 3, 4

Per cell: **R** = a movement rule is as good as the best balanced draw found (on balance + all mixing fields); **D a/b (rule c/d)** = use the explicit draw from schemes.json (max meet/max follow a/b; the best lane-pair-balanced rule only manages c/d).  The rules column gives one rule in plain words covering the R cells.

| M×K | B=3 | B=4 | B=5 | B=6 | rule for the R cells |
|---|---|---|---|---|---|
| 3×2 | R | D 1/1 (rule 2/2) | D 1/1 (rule 2/2) | D 2/2 (rule 2/2) | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 1 pair right, keep position |
| 4×2 | D 1/1 (rule 2/2) | D 1/1 (rule 2/2) | D 1/1 (rule 3/3) | D 1/1 (rule 3/3) |  |
| 5×2 | R | R | R | D 1/1 (rule 2/2) | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 1 pair right, keep position |
| 6×2 | R | D 1/1 (rule 2/2) | D 1/1 (rule 2/2) | D 1/1 (rule 2/2) | 1st (left lane): move 2 pairs right, keep position; 2nd (right lane): move 1 pair right, keep position |
| 7×2 | R | R | R | R | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 1 pair right, keep position |
| 8×2 | R | R | D 1/1 (rule 2/2) | D 1/1 (rule 2/2) | 1st (left lane): move 2 pairs right, keep position; 2nd (right lane): move 1 pair right, keep position |
| 9×2 | R | R | R | R | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 1 pair right, keep position |
| 10×2 | R | R | R | D 1/1 (rule 2/2) | 1st (left lane): move 2 pairs right, keep position; 2nd (right lane): move 1 pair right, keep position |
| 3×3 | R | D 2/1 (rule 3/3) | D 2/1 (rule 3/3) | D 2/2 (rule 3/3) | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 1 pair right, bowl 3rd (left lane); 3rd (left lane): move 1 pair right, bowl 2nd (right lane) |
| 4×3 | D 1/1 (rule 2/2) | D 1/1 (rule 4/2) | D 2/1 (rule 3/3) | D 2/1 (rule 2/2) |  |
| 5×3 | R | R | R | D 2/1 (rule 2/2) | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 2 pairs right, keep position; 3rd (left lane): move 1 pair right, keep position |
| 6×3 | R | D 1/1 (rule 2/2) | D 1/1 (rule 3/3) | D 1/1 (rule 3/3) | 1st (left lane): move 3 pairs right, bowl 2nd (right lane); 2nd (right lane): move 2 pairs right, bowl 3rd (left lane); 3rd (left lane): move 1 pair right, bowl 1st (left lane) |
| 7×3 | R | R | R | R | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 2 pairs right, keep position; 3rd (left lane): move 1 pair right, keep position |
| 8×3 | R | R | D 1/1 (rule 2/2) | D 1/1 (rule 2/2) | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 2 pairs right, keep position; 3rd (left lane): move 1 pair right, keep position |
| 9×3 | R | D 1/1 (rule 2/2) | D 1/1 (rule 2/2) | D 1/1 (rule 2/2) | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 3 pairs right, keep position; 3rd (left lane): move 1 pair right, keep position |
| 10×3 | R | R | R | D 1/1 (rule 2/2) | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 2 pairs right, keep position; 3rd (left lane): move 1 pair right, keep position |
| 3×4 | R | D 2/1 (rule 2/1) | D 2/1 (rule 3/2) | D 2/1 (rule 3/2) | 1st (left lane): move 1 pair left, bowl 2nd (right lane); 2nd (right lane): move 1 pair left, bowl 1st (left lane); 3rd (left lane): move 1 pair right, bowl 4th (right lane); 4th (right lane): move 1 pair right, bowl 3rd (left lane) |
| 4×4 | D 2/1 (rule 2/1) | D 2/1 (rule 2/1) | D 2/1 (rule 3/1) | D 2/1 (rule 3/1) |  |
| 5×4 | R | R | R | D 2/1 (rule 2/2) | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 2 pairs left, keep position; 3rd (left lane): move 2 pairs right, keep position; 4th (right lane): move 1 pair right, keep position |
| 6×4 | R | D 1/1 (rule 2/1) | D 1/1 (rule 3/2) | D 2/1 (rule 3/2) | 1st (left lane): move 3 pairs right, bowl 2nd (right lane); 2nd (right lane): move 1 pair left, bowl 3rd (left lane); 3rd (left lane): move 2 pairs right, bowl 4th (right lane); 4th (right lane): move 1 pair right, bowl 1st (left lane) |
| 7×4 | R | R | R | R | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 2 pairs left, keep position; 3rd (left lane): move 2 pairs right, keep position; 4th (right lane): move 1 pair right, keep position |
| 8×4 | R | R | D 1/1 (rule 2/2) | D 1/1 (rule 2/2) | 1st (left lane): move 2 pairs left, bowl 2nd (right lane); 2nd (right lane): move 1 pair left, bowl 3rd (left lane); 3rd (left lane): move 2 pairs right, bowl 4th (right lane); 4th (right lane): move 1 pair right, bowl 1st (left lane) |
| 9×4 | R | R | D 1/1 (rule 2/1) | D 1/1 (rule 2/1) | 1st (left lane): move 2 pairs left, bowl 2nd (right lane); 2nd (right lane): move 1 pair left, bowl 3rd (left lane); 3rd (left lane): move 2 pairs right, bowl 4th (right lane); 4th (right lane): move 1 pair right, bowl 1st (left lane) |
| 10×4 | R | R | R | D 1/1 (rule 2/2) | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 2 pairs left, keep position; 3rd (left lane): move 2 pairs right, keep position; 4th (right lane): move 1 pair right, keep position |

### Universal rules (one rule, optimal among rules for every B up to the limit)

| M×K | optimal among rules for B ≤ | rule |
|---|---|---|
| 3×2 | 12 | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 1 pair right, keep position |
| 4×2 | 2 | 1st (left lane): move 2 pairs right, keep position; 2nd (right lane): move 1 pair right, keep position |
| 5×2 | 12 | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 1 pair right, keep position |
| 6×2 | 3 | 1st (left lane): move 2 pairs right, keep position; 2nd (right lane): move 1 pair right, keep position |
| 7×2 | 12 | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 1 pair right, keep position |
| 8×2 | 4 | 1st (left lane): move 2 pairs right, keep position; 2nd (right lane): move 1 pair right, keep position |
| 9×2 | 12 | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 1 pair right, keep position |
| 10×2 | 5 | 1st (left lane): move 2 pairs right, keep position; 2nd (right lane): move 1 pair right, keep position |
| 3×3 | 1 | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 1 pair right, keep position; 3rd (left lane): stay on the pair, keep position |
| 4×3 | 3 | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 2 pairs right, bowl 3rd (left lane); 3rd (left lane): move 1 pair right, bowl 2nd (right lane) |
| 5×3 | 12 | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 2 pairs right, keep position; 3rd (left lane): move 1 pair right, keep position |
| 6×3 | 2 | 1st (left lane): move 3 pairs right, keep position; 2nd (right lane): move 2 pairs right, keep position; 3rd (left lane): move 1 pair right, keep position |
| 7×3 | 12 | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 2 pairs right, keep position; 3rd (left lane): move 1 pair right, keep position |
| 8×3 | 4 | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 2 pairs right, keep position; 3rd (left lane): move 1 pair right, keep position |
| 9×3 | 3 | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 3 pairs right, keep position; 3rd (left lane): move 1 pair right, keep position |
| 10×3 | 5 | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 2 pairs right, keep position; 3rd (left lane): move 1 pair right, keep position |
| 3×4 | 1 | 1st (left lane): move 1 pair left, bowl 2nd (right lane); 2nd (right lane): move 1 pair right, bowl 3rd (left lane); 3rd (left lane): stay on the pair, bowl 4th (right lane); 4th (right lane): stay on the pair, bowl 1st (left lane) |
| 4×4 | 2 | 1st (left lane): move 2 pairs right, keep position; 2nd (right lane): move 1 pair left, bowl 3rd (left lane); 3rd (left lane): move 2 pairs right, bowl 2nd (right lane); 4th (right lane): move 1 pair right, keep position |
| 5×4 | 12 | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 2 pairs left, keep position; 3rd (left lane): move 2 pairs right, keep position; 4th (right lane): move 1 pair right, keep position |
| 6×4 | 2 | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 2 pairs left, keep position; 3rd (left lane): move 2 pairs right, bowl 4th (right lane); 4th (right lane): move 1 pair right, bowl 3rd (left lane) |
| 7×4 | 12 | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 2 pairs left, keep position; 3rd (left lane): move 2 pairs right, keep position; 4th (right lane): move 1 pair right, keep position |
| 8×4 | 2 | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 2 pairs left, keep position; 3rd (left lane): move 2 pairs right, bowl 4th (right lane); 4th (right lane): move 1 pair right, bowl 3rd (left lane) |
| 9×4 | 3 | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 3 pairs right, keep position; 3rd (left lane): move 2 pairs right, keep position; 4th (right lane): move 1 pair right, keep position |
| 10×4 | 2 | 1st (left lane): move 2 pairs left, keep position; 2nd (right lane): move 3 pairs left, keep position; 3rd (left lane): move 2 pairs right, bowl 4th (right lane); 4th (right lane): move 1 pair right, bowl 3rd (left lane) |
| 3×5 | 1 | 1st (left lane): move 1 pair right, keep position; 2nd (right lane): move 1 pair left, bowl 3rd (left lane); 3rd (left lane): move 1 pair right, bowl 4th (right lane); 4th (right lane): stay on the pair, bowl 5th (left lane); 5th (left lane): stay on the pair, bowl 2nd (right lane) |
| 4×5 | 1 | 1st (left lane): move 2 pairs right, bowl 2nd (right lane); 2nd (right lane): stay on the pair, bowl 3rd (left lane); 3rd (left lane): move 1 pair left, bowl 4th (right lane); 4th (right lane): move 1 pair right, bowl 5th (left lane); 5th (left lane): stay on the pair, bowl 1st (left lane) |
| 5×5 | 1 | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 2 pairs left, keep position; 3rd (left lane): move 2 pairs right, keep position; 4th (right lane): move 1 pair right, keep position; 5th (left lane): stay on the pair, keep position |
| 6×5 | 1 | 1st (left lane): move 2 pairs left, keep position; 2nd (right lane): move 1 pair left, bowl 3rd (left lane); 3rd (left lane): move 1 pair right, bowl 2nd (right lane); 4th (right lane): move 1 pair right, bowl 5th (left lane); 5th (left lane): stay on the pair, bowl 4th (right lane) |
| 7×5 | 12 | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 2 pairs left, keep position; 3rd (left lane): move 3 pairs right, keep position; 4th (right lane): move 2 pairs right, keep position; 5th (left lane): move 1 pair right, keep position |
| 8×5 | 2 | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 2 pairs left, keep position; 3rd (left lane): move 3 pairs left, keep position; 4th (right lane): move 2 pairs right, bowl 5th (left lane); 5th (left lane): move 1 pair right, bowl 4th (right lane) |
| 9×5 | 3 | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 2 pairs left, keep position; 3rd (left lane): move 3 pairs right, keep position; 4th (right lane): move 2 pairs right, keep position; 5th (left lane): move 1 pair right, keep position |
| 10×5 | 2 | 1st (left lane): move 1 pair left, keep position; 2nd (right lane): move 2 pairs left, keep position; 3rd (left lane): move 1 pair right, keep position; 4th (right lane): move 3 pairs right, bowl 5th (left lane); 5th (left lane): move 2 pairs right, bowl 4th (right lane) |

### Where lane-pair balance forces worse mixing than the unconstrained best found

Mixing tuple = (max meet, max follow, repeats, follow repeats, max unordered follow, unordered follow repeats, -min meet).

- 3×3 B=2: balanced [2, 1, 3, 0, 2, 3, 0] vs unconstrained [1, 1, 0, 0, 1, 0, 0]
- 3×3 B=3: balanced [3, 2, 6, 3, 3, 6, 0] vs unconstrained [1, 1, 0, 0, 1, 0, 0]
- 3×3 B=4: balanced [2, 1, 9, 0, 2, 9, 0] vs unconstrained [1, 1, 0, 0, 1, 0, -1]
- 3×3 B=5: balanced [2, 1, 12, 0, 2, 12, 0] vs unconstrained [2, 1, 9, 0, 2, 9, -1]
- 3×3 B=6: balanced [2, 2, 18, 3, 2, 18, -1] vs unconstrained [2, 1, 18, 0, 2, 18, -1]
- 4×3 B=12: balanced [3, 2, 78, 14, 3, 78, -2] vs unconstrained [3, 2, 78, 13, 3, 78, -2]
- 5×3 B=6: balanced [2, 1, 1, 0, 2, 1, 0] vs unconstrained [1, 1, 0, 0, 1, 0, 0]
- 5×3 B=7: balanced [2, 1, 5, 0, 2, 5, 0] vs unconstrained [1, 1, 0, 0, 1, 0, -1]
- 6×3 B=7: balanced [2, 1, 2, 0, 2, 2, 0] vs unconstrained [1, 1, 0, 0, 1, 0, 0]
- 6×3 B=12: balanced [2, 2, 64, 2, 2, 64, 0] vs unconstrained [2, 2, 63, 1, 2, 63, -1]
- 7×3 B=8: balanced [2, 1, 1, 0, 2, 1, 0] vs unconstrained [1, 1, 0, 0, 1, 0, 0]
- 7×3 B=12: balanced [2, 1, 43, 0, 2, 43, 0] vs unconstrained [2, 1, 42, 0, 2, 42, -1]
- 8×3 B=9: balanced [2, 1, 1, 0, 2, 1, 0] vs unconstrained [1, 1, 0, 0, 1, 0, 0]
- 8×3 B=10: balanced [2, 1, 4, 0, 2, 4, 0] vs unconstrained [1, 1, 0, 0, 1, 0, 0]
- 9×3 B=10: balanced [2, 1, 3, 0, 2, 3, 0] vs unconstrained [1, 1, 0, 0, 1, 0, 0]
- 9×3 B=11: balanced [2, 1, 5, 0, 2, 5, 0] vs unconstrained [1, 1, 0, 0, 1, 0, 0]
- 9×3 B=12: balanced [2, 1, 9, 0, 2, 9, 0] vs unconstrained [2, 1, 1, 0, 2, 1, 0]
- 10×3 B=9: balanced [2, 1, 2, 0, 2, 2, 0] vs unconstrained [1, 1, 0, 0, 1, 0, 0]
- 10×3 B=10: balanced [2, 1, 11, 0, 2, 11, 0] vs unconstrained [1, 1, 0, 0, 1, 0, 0]
- 10×3 B=11: balanced [2, 1, 2, 0, 2, 2, 0] vs unconstrained [1, 1, 0, 0, 1, 0, 0]
- 10×3 B=12: balanced [2, 1, 4, 0, 2, 4, 0] vs unconstrained [1, 1, 0, 0, 1, 0, 0]
- 3×4 B=2: balanced [2, 1, 6, 0, 1, 0, 0] vs unconstrained [2, 1, 3, 0, 1, 0, 0]
- 3×4 B=3: balanced [3, 1, 12, 0, 1, 0, 0] vs unconstrained [2, 1, 9, 0, 1, 0, 0]
- 3×4 B=4: balanced [2, 1, 24, 0, 2, 2, 0] vs unconstrained [2, 1, 18, 0, 2, 2, 0]
- 3×4 B=5: balanced [2, 1, 36, 0, 2, 8, 0] vs unconstrained [2, 1, 30, 0, 2, 6, 0]
- 3×4 B=6: balanced [2, 1, 54, 0, 2, 18, 0] vs unconstrained [2, 1, 45, 0, 2, 9, 0]
- 3×4 B=8: balanced [3, 1, 78, 0, 2, 30, -1] vs unconstrained [3, 1, 78, 0, 2, 30, -2]
- 3×4 B=10: balanced [3, 2, 114, 5, 3, 55, -2] vs unconstrained [3, 2, 114, 3, 3, 54, -2]
- 3×4 B=11: balanced [4, 2, 132, 10, 3, 66, -2] vs unconstrained [3, 2, 132, 8, 3, 66, -3]
- 3×4 B=12: balanced [4, 2, 150, 12, 3, 78, -2] vs unconstrained [4, 2, 150, 12, 3, 78, -3]
- 4×4 B=2: balanced [2, 1, 4, 0, 1, 0, 0] vs unconstrained [1, 1, 0, 0, 1, 0, 0]
- 4×4 B=3: balanced [2, 1, 12, 0, 1, 0, 0] vs unconstrained [1, 1, 0, 0, 1, 0, 0]
- 4×4 B=4: balanced [2, 1, 24, 0, 2, 8, 0] vs unconstrained [1, 1, 0, 0, 1, 0, 0]
- 4×4 B=5: balanced [2, 1, 24, 0, 2, 1, 0] vs unconstrained [1, 1, 0, 0, 1, 0, -1]
- 4×4 B=6: balanced [2, 1, 29, 0, 2, 1, 0] vs unconstrained [2, 1, 24, 0, 2, 2, -1]
- 4×4 B=7: balanced [2, 1, 50, 0, 2, 6, 0] vs unconstrained [2, 1, 48, 0, 2, 5, -1]
- 4×4 B=9: balanced [3, 1, 96, 0, 2, 25, -1] vs unconstrained [2, 1, 96, 0, 2, 24, -1]
- 4×4 B=10: balanced [3, 1, 120, 0, 2, 40, -1] vs unconstrained [2, 1, 120, 0, 2, 40, -2]
- 4×4 B=11: balanced [3, 1, 144, 0, 2, 56, -1] vs unconstrained [3, 1, 144, 0, 2, 56, -2]
- 5×4 B=8: balanced [2, 1, 52, 0, 2, 2, 0] vs unconstrained [2, 1, 50, 0, 2, 2, -1]
- 5×4 B=9: balanced [2, 1, 83, 0, 2, 10, 0] vs unconstrained [2, 1, 80, 0, 2, 8, -1]
- 5×4 B=10: balanced [2, 1, 110, 0, 2, 33, -1] vs unconstrained [2, 1, 110, 0, 2, 17, -1]
- 5×4 B=11: balanced [3, 1, 140, 0, 2, 33, -1] vs unconstrained [2, 1, 140, 0, 2, 32, -1]
- 6×4 B=6: balanced [2, 1, 17, 0, 1, 0, 0] vs unconstrained [2, 1, 1, 0, 1, 0, 0]
- 6×4 B=7: balanced [2, 1, 19, 0, 1, 0, 0] vs unconstrained [2, 1, 8, 0, 1, 0, 0]
- 6×4 B=8: balanced [2, 1, 34, 0, 1, 0, 0] vs unconstrained [2, 1, 24, 0, 1, 0, 0]
- 6×4 B=9: balanced [2, 1, 57, 0, 1, 0, 0] vs unconstrained [2, 1, 49, 0, 1, 0, 0]
- 6×4 B=10: balanced [2, 1, 91, 0, 2, 4, 0] vs unconstrained [2, 1, 84, 0, 2, 3, -1]
- 6×4 B=11: balanced [2, 1, 126, 0, 2, 17, 0] vs unconstrained [2, 1, 120, 0, 2, 13, -1]
- 6×4 B=12: balanced [3, 1, 156, 0, 2, 36, -1] vs unconstrained [2, 1, 156, 0, 2, 26, -1]
- 7×4 B=8: balanced [2, 1, 9, 0, 1, 0, 0] vs unconstrained [2, 1, 8, 0, 1, 0, 0]
- 7×4 B=10: balanced [2, 1, 59, 0, 2, 2, 0] vs unconstrained [2, 1, 50, 0, 1, 0, 0]
- 7×4 B=11: balanced [2, 1, 91, 0, 2, 3, 0] vs unconstrained [2, 1, 84, 0, 1, 0, -1]
- 7×4 B=12: balanced [2, 1, 134, 0, 2, 11, 0] vs unconstrained [2, 1, 126, 0, 2, 5, -1]
- 8×4 B=9: balanced [2, 1, 36, 0, 1, 0, 0] vs unconstrained [2, 1, 9, 0, 1, 0, 0]
- 8×4 B=10: balanced [2, 1, 49, 0, 1, 0, 0] vs unconstrained [2, 1, 24, 0, 1, 0, 0]
- 8×4 B=11: balanced [2, 1, 65, 0, 1, 0, 0] vs unconstrained [2, 1, 48, 0, 1, 0, 0]
- 8×4 B=12: balanced [2, 1, 100, 0, 1, 0, 0] vs unconstrained [2, 1, 84, 0, 1, 0, 0]
- 9×4 B=10: balanced [2, 1, 41, 0, 1, 0, 0] vs unconstrained [2, 1, 9, 0, 1, 0, 0]
- 9×4 B=11: balanced [2, 1, 47, 0, 1, 0, 0] vs unconstrained [2, 1, 23, 0, 1, 0, 0]
- 9×4 B=12: balanced [2, 1, 59, 0, 1, 0, 0] vs unconstrained [2, 1, 46, 0, 1, 0, 0]
- 10×4 B=8: balanced [2, 1, 7, 0, 1, 0, 0] vs unconstrained [1, 1, 0, 0, 1, 0, 0]
- 10×4 B=9: balanced [2, 1, 32, 0, 1, 0, 0] vs unconstrained [1, 1, 0, 0, 1, 0, 0]
- 10×4 B=10: balanced [2, 1, 56, 0, 1, 0, 0] vs unconstrained [2, 1, 1, 0, 1, 0, 0]
- 10×4 B=11: balanced [2, 1, 56, 0, 1, 0, 0] vs unconstrained [2, 1, 9, 0, 1, 0, 0]
- 10×4 B=12: balanced [2, 1, 62, 0, 1, 0, 0] vs unconstrained [2, 1, 22, 0, 1, 0, 0]
- 3×5 B=2: balanced [2, 1, 12, 0, 1, 0, 0] vs unconstrained [2, 1, 6, 0, 1, 0, 0]
- 3×5 B=3: balanced [3, 1, 24, 0, 1, 0, 0] vs unconstrained [2, 1, 18, 0, 1, 0, 0]
- 3×5 B=4: balanced [3, 1, 34, 0, 1, 0, 0] vs unconstrained [2, 1, 36, 0, 1, 0, 0]
- 3×5 B=9: balanced [3, 1, 174, 0, 2, 39, 0] vs unconstrained [3, 1, 165, 0, 2, 30, -1]
- 3×5 B=11: balanced [4, 1, 225, 0, 2, 61, -2] vs unconstrained [4, 1, 225, 0, 2, 60, -2]
- 3×5 B=12: balanced [4, 2, 255, 2, 3, 75, -2] vs unconstrained [4, 2, 255, 1, 3, 76, -2]
- 4×5 B=2: balanced [2, 1, 8, 0, 1, 0, 0] vs unconstrained [2, 1, 4, 0, 1, 0, 0]
- 4×5 B=3: balanced [2, 1, 24, 0, 1, 0, 0] vs unconstrained [2, 1, 12, 0, 1, 0, 0]
- 4×5 B=4: balanced [2, 1, 48, 0, 1, 0, 0] vs unconstrained [2, 1, 24, 0, 1, 0, 0]
- 4×5 B=5: balanced [2, 1, 60, 0, 1, 0, 0] vs unconstrained [2, 1, 40, 0, 1, 0, 0]
- 4×5 B=6: balanced [2, 1, 80, 0, 1, 0, 0] vs unconstrained [2, 1, 60, 0, 1, 0, 0]
- 4×5 B=7: balanced [3, 1, 95, 0, 1, 0, 0] vs unconstrained [2, 1, 91, 0, 1, 0, 0]
- 4×5 B=8: balanced [3, 1, 131, 0, 1, 0, 0] vs unconstrained [3, 1, 130, 0, 1, 0, -1]
- 4×5 B=9: balanced [3, 1, 170, 0, 2, 3, -1] vs unconstrained [3, 1, 170, 0, 2, 1, -1]
- 4×5 B=12: balanced [4, 1, 290, 0, 2, 50, -1] vs unconstrained [3, 1, 290, 0, 2, 50, -1]
- 5×5 B=2: balanced [2, 1, 5, 0, 1, 0, 0] vs unconstrained [1, 1, 0, 0, 1, 0, 0]
- 5×5 B=3: balanced [2, 1, 15, 0, 1, 0, 0] vs unconstrained [1, 1, 0, 0, 1, 0, 0]
- 5×5 B=4: balanced [2, 1, 30, 0, 1, 0, 0] vs unconstrained [1, 1, 0, 0, 1, 0, 0]
- 5×5 B=5: balanced [2, 1, 89, 0, 1, 0, 0] vs unconstrained [1, 1, 0, 0, 1, 0, 0]
- 5×5 B=6: balanced [2, 1, 52, 0, 1, 0, 0] vs unconstrained [1, 1, 0, 0, 1, 0, -1]
- 5×5 B=7: balanced [2, 1, 73, 0, 1, 0, 0] vs unconstrained [2, 1, 50, 0, 1, 0, -1]
- 5×5 B=8: balanced [2, 1, 111, 0, 1, 0, 0] vs unconstrained [2, 1, 101, 0, 1, 0, 0]
- 5×5 B=9: balanced [3, 1, 151, 0, 1, 0, 0] vs unconstrained [2, 1, 151, 0, 1, 0, 0]
- 5×5 B=10: balanced [3, 1, 203, 0, 1, 0, 0] vs unconstrained [3, 1, 201, 0, 1, 0, 0]
- 6×5 B=4: balanced [2, 1, 6, 0, 1, 0, 0] vs unconstrained [1, 1, 0, 0, 1, 0, 0]
- 6×5 B=5: balanced [2, 1, 22, 0, 1, 0, 0] vs unconstrained [1, 1, 0, 0, 1, 0, 0]
- 6×5 B=6: balanced [2, 1, 41, 0, 1, 0, 0] vs unconstrained [2, 1, 6, 0, 1, 0, 0]
- 6×5 B=7: balanced [2, 1, 51, 0, 1, 0, 0] vs unconstrained [2, 1, 33, 0, 1, 0, 0]
- 6×5 B=8: balanced [2, 1, 83, 0, 1, 0, 0] vs unconstrained [2, 1, 65, 0, 1, 0, 0]
- 6×5 B=9: balanced [2, 1, 124, 0, 1, 0, 0] vs unconstrained [2, 1, 110, 0, 1, 0, 0]
- 6×5 B=10: balanced [2, 1, 182, 0, 1, 0, 0] vs unconstrained [2, 1, 166, 0, 1, 0, 0]
- 6×5 B=11: balanced [3, 1, 228, 0, 1, 0, 0] vs unconstrained [2, 1, 225, 0, 1, 0, -1]
- 6×5 B=12: balanced [3, 1, 289, 0, 1, 0, 0] vs unconstrained [3, 1, 287, 0, 1, 0, 0]
- 7×5 B=10: balanced [2, 1, 150, 0, 1, 0, 0] vs unconstrained [2, 1, 122, 0, 1, 0, 0]
- 7×5 B=11: balanced [2, 2, 280, 140, 2, 140, 0] vs unconstrained [2, 1, 180, 0, 1, 0, 0]
- 7×5 B=12: balanced [2, 2, 350, 175, 2, 175, 0] vs unconstrained [2, 1, 247, 0, 1, 0, 0]
- 8×5 B=9: balanced [2, 1, 96, 0, 1, 0, 0] vs unconstrained [2, 1, 46, 0, 1, 0, 0]
- 8×5 B=10: balanced [2, 1, 121, 0, 1, 0, 0] vs unconstrained [2, 1, 84, 0, 1, 0, 0]
- 8×5 B=11: balanced [2, 1, 169, 0, 1, 0, 0] vs unconstrained [2, 1, 133, 0, 1, 0, 0]
- 8×5 B=12: balanced [2, 1, 228, 0, 1, 0, 0] vs unconstrained [2, 1, 194, 0, 1, 0, 0]
- 9×5 B=10: balanced [2, 1, 119, 0, 1, 0, 0] vs unconstrained [2, 1, 52, 0, 1, 0, 0]
- 9×5 B=11: balanced [2, 1, 130, 0, 1, 0, 0] vs unconstrained [2, 1, 92, 0, 1, 0, 0]
- 9×5 B=12: balanced [2, 1, 186, 0, 1, 0, 0] vs unconstrained [2, 1, 141, 0, 1, 0, 0]
- 10×5 B=7: balanced [2, 1, 7, 0, 1, 0, 0] vs unconstrained [1, 1, 0, 0, 1, 0, 0]
- 10×5 B=8: balanced [2, 1, 33, 0, 1, 0, 0] vs unconstrained [2, 1, 1, 0, 1, 0, 0]
- 10×5 B=9: balanced [2, 1, 82, 0, 1, 0, 0] vs unconstrained [2, 1, 10, 0, 1, 0, 0]
- 10×5 B=10: balanced [2, 1, 139, 0, 1, 0, 0] vs unconstrained [2, 1, 30, 0, 1, 0, 0]
- 10×5 B=11: balanced [2, 1, 145, 0, 1, 0, 0] vs unconstrained [2, 1, 59, 0, 1, 0, 0]
- 10×5 B=12: balanced [2, 1, 168, 0, 1, 0, 0] vs unconstrained [2, 1, 101, 0, 1, 0, 0]

### Open: max meetings or max follows not proven optimal

Tuple = (pair_spread, max_meet, max_follow, repeats, follow_repeats, max_ufollow, ufollow_repeats, -min_meet); bound = simple counting bound, or z3 where run.

- 3×3 B=3: best [0, 3, 2, 6, 3, 3, 6, 0] vs bound [0, 3, 1, 0, 0, 1, 0, 0] (first gap: max_follow)
- 3×3 B=6: best [0, 2, 2, 18, 3, 2, 18, -1] vs bound [0, 2, 1, 18, 0, 2, 18, -1] (first gap: max_follow)
- 4×3 B=9: best [1, 2, 2, 42, 3, 2, 42, -1] vs bound [1, 2, 1, 42, 0, 2, 42, -1] (first gap: max_follow)
- 4×3 B=10: best [1, 2, 2, 54, 2, 2, 54, -1] vs bound [1, 2, 1, 54, 0, 2, 54, -1] (first gap: max_follow)
- 4×3 B=11: best [1, 2, 2, 66, 5, 2, 66, -2] vs bound [1, 2, 1, 66, 0, 2, 66, -2] (first gap: max_follow)
- 5×3 B=6: best [1, 2, 1, 1, 0, 2, 1, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 5×3 B=7: best [1, 2, 1, 5, 0, 2, 5, 0] vs bound [1, 1, 1, 0, 0, 1, 0, -1] (first gap: max_meet)
- 5×3 B=11: best [1, 2, 2, 60, 3, 2, 60, -1] vs bound [1, 2, 1, 60, 0, 2, 60, -1] (first gap: max_follow)
- 5×3 B=12: best [1, 2, 2, 75, 3, 2, 75, -1] vs bound [1, 2, 1, 75, 0, 2, 75, -1] (first gap: max_follow)
- 6×3 B=7: best [1, 2, 1, 2, 0, 2, 2, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 6×3 B=8: best [1, 2, 1, 1, 0, 2, 1, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 6×3 B=12: best [0, 2, 2, 64, 2, 2, 64, 0] vs bound [0, 2, 1, 63, 0, 2, 63, -1] (first gap: max_follow)
- 7×3 B=8: best [1, 2, 1, 1, 0, 2, 1, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 7×3 B=10: best [1, 2, 1, 5, 0, 2, 5, 0] vs bound [1, 1, 1, 0, 0, 1, 0, -1] (first gap: max_meet)
- 8×3 B=9: best [1, 2, 1, 1, 0, 2, 1, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 8×3 B=10: best [1, 2, 1, 4, 0, 2, 4, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 8×3 B=11: best [1, 2, 1, 3, 0, 2, 3, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 9×3 B=10: best [1, 2, 1, 3, 0, 2, 3, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 9×3 B=11: best [1, 2, 1, 5, 0, 2, 5, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 9×3 B=12: best [1, 2, 1, 9, 0, 2, 9, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 10×3 B=9: best [1, 2, 1, 2, 0, 2, 2, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 10×3 B=10: best [0, 2, 1, 11, 0, 2, 11, 0] vs bound [0, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 10×3 B=11: best [1, 2, 1, 2, 0, 2, 2, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 10×3 B=12: best [1, 2, 1, 4, 0, 2, 4, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 3×4 B=7: best [1, 3, 1, 60, 0, 2, 18, -1] vs bound [1, 2, 1, 60, 0, 2, 18, -1] (first gap: max_meet)
- 3×4 B=10: best [1, 3, 2, 114, 5, 3, 55, -2] vs bound [1, 3, 1, 114, 0, 2, 54, -2] (first gap: max_follow)
- 3×4 B=11: best [1, 4, 2, 132, 10, 3, 66, -2] vs bound [1, 3, 1, 132, 0, 2, 66, -3] (first gap: max_meet)
- 4×4 B=9: best [1, 3, 1, 96, 0, 2, 25, -1] vs bound [1, 2, 1, 96, 0, 2, 24, -1] (first gap: max_meet)
- 4×4 B=10: best [1, 3, 1, 120, 0, 2, 40, -1] vs bound [1, 2, 1, 120, 0, 2, 40, -2] (first gap: max_meet)
- 5×4 B=11: best [1, 3, 1, 140, 0, 2, 33, -1] vs bound [1, 2, 1, 140, 0, 2, 30, -1] (first gap: max_meet)
- 5×4 B=12: best [1, 3, 1, 170, 0, 2, 50, -1] vs bound [1, 2, 1, 170, 0, 2, 50, -1] (first gap: max_meet)
- 6×4 B=6: best [0, 2, 1, 17, 0, 1, 0, 0] vs bound [0, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 6×4 B=7: best [1, 2, 1, 19, 0, 1, 0, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 6×4 B=12: best [0, 3, 1, 156, 0, 2, 36, -1] vs bound [0, 2, 1, 156, 0, 2, 12, -1] (first gap: max_meet)
- 7×4 B=8: best [1, 2, 1, 9, 0, 1, 0, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 7×4 B=9: best [1, 2, 1, 16, 0, 1, 0, 0] vs bound [1, 1, 1, 0, 0, 1, 0, -1] (first gap: max_meet)
- 8×4 B=9: best [1, 2, 1, 36, 0, 1, 0, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 8×4 B=10: best [1, 2, 1, 49, 0, 1, 0, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 9×4 B=10: best [1, 2, 1, 41, 0, 1, 0, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 9×4 B=11: best [1, 2, 1, 47, 0, 1, 0, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 10×4 B=8: best [1, 2, 1, 7, 0, 1, 0, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 10×4 B=9: best [1, 2, 1, 32, 0, 1, 0, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 10×4 B=10: best [0, 2, 1, 56, 0, 1, 0, 0] vs bound [0, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 10×4 B=11: best [1, 2, 1, 56, 0, 1, 0, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 10×4 B=12: best [1, 2, 1, 62, 0, 1, 0, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 3×5 B=10: best [1, 4, 1, 195, 0, 2, 45, -2] vs bound [1, 3, 1, 195, 0, 2, 45, -2] (first gap: max_meet)
- 3×5 B=12: best [0, 4, 2, 255, 2, 3, 75, -2] vs bound [0, 4, 1, 255, 0, 2, 75, -3] (first gap: max_follow)
- 4×5 B=7: best [1, 3, 1, 95, 0, 1, 0, 0] vs bound [1, 2, 1, 90, 0, 1, 0, -1] (first gap: max_meet)
- 4×5 B=8: best [0, 3, 1, 131, 0, 1, 0, 0] vs bound [0, 2, 1, 130, 0, 1, 0, -1] (first gap: max_meet)
- 4×5 B=9: best [1, 3, 1, 170, 0, 2, 3, -1] vs bound [1, 2, 1, 170, 0, 1, 0, -1] (first gap: max_meet)
- 4×5 B=12: best [0, 4, 1, 290, 0, 2, 50, -1] vs bound [0, 3, 1, 290, 0, 2, 50, -2] (first gap: max_meet)
- 5×5 B=9: best [1, 3, 1, 151, 0, 1, 0, 0] vs bound [1, 2, 1, 150, 0, 1, 0, -1] (first gap: max_meet)
- 5×5 B=10: best [0, 3, 1, 203, 0, 1, 0, 0] vs bound [0, 2, 1, 200, 0, 1, 0, -1] (first gap: max_meet)
- 5×5 B=11: best [1, 3, 1, 250, 0, 2, 3, -1] vs bound [1, 2, 1, 250, 0, 1, 0, -1] (first gap: max_meet)
- 5×5 B=12: best [1, 3, 1, 300, 0, 2, 9, -1] vs bound [1, 2, 1, 300, 0, 1, 0, -2] (first gap: max_meet)
- 6×5 B=4: best [1, 2, 1, 6, 0, 1, 0, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 6×5 B=5: best [1, 2, 1, 22, 0, 1, 0, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 6×5 B=6: best [0, 2, 1, 41, 0, 1, 0, 0] vs bound [0, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 6×5 B=7: best [1, 2, 1, 51, 0, 1, 0, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 6×5 B=11: best [1, 3, 1, 228, 0, 1, 0, 0] vs bound [1, 2, 1, 225, 0, 1, 0, -1] (first gap: max_meet)
- 6×5 B=12: best [0, 3, 1, 289, 0, 1, 0, 0] vs bound [0, 2, 1, 285, 0, 1, 0, -1] (first gap: max_meet)
- 7×5 B=8: best [1, 2, 1, 16, 0, 1, 0, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 7×5 B=11: best [1, 2, 2, 280, 140, 2, 140, 0] vs bound [1, 2, 1, 175, 0, 1, 0, -1] (first gap: max_follow)
- 7×5 B=12: best [1, 2, 2, 350, 175, 2, 175, 0] vs bound [1, 2, 1, 245, 0, 1, 0, -1] (first gap: max_follow)
- 8×5 B=9: best [1, 2, 1, 96, 0, 1, 0, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 9×5 B=10: best [1, 2, 1, 119, 0, 1, 0, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 9×5 B=11: best [1, 2, 1, 130, 0, 1, 0, 0] vs bound [1, 1, 1, 0, 0, 1, 0, -1] (first gap: max_meet)
- 10×5 B=7: best [1, 2, 1, 7, 0, 1, 0, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 10×5 B=8: best [1, 2, 1, 33, 0, 1, 0, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 10×5 B=9: best [1, 2, 1, 82, 0, 1, 0, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 10×5 B=10: best [0, 2, 1, 139, 0, 1, 0, 0] vs bound [0, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 10×5 B=11: best [1, 2, 1, 145, 0, 1, 0, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)
- 10×5 B=12: best [1, 2, 1, 168, 0, 1, 0, 0] vs bound [1, 1, 1, 0, 0, 1, 0, 0] (first gap: max_meet)


## Files

* `model.py`: draw model, follow relation, evaluator (`evaluate`), rule →
  draw (`rule_draw`), structural exclusion (`rule_exclusion`), plain-words
  rule description.
* `rulesearch.c`: exhaustive search over all movement rules (all d ∈ Z_M^K,
  all π ∈ S_K) for each (M, K). It works on classes (t, u, offset), using
  translation invariance. It writes the best rule for every B ≤ 12 and the
  "universal" rule (optimal among rules for the longest run of B). Output is in
  `results/rules/`.
* `anneal.c` and `optimum.py`: unrestricted draws. Lower bounds come from
  `optimum.bounds`. The anneal has two phases. Phase 1 decides who shares
  which pair, with lane-pair balance as a hard constraint, using swap, group
  swap and balance-preserving double-swap moves. Phase 2 sets the bowling
  order to optimise following, side and position. Runs start from the best
  rule, from the GF(q) construction or from scratch. Output is in
  `results/opt/`. `results/opt_free/` holds the earlier runs without the balance
  constraint, used for the "balance costs mixing" comparison.
* `exact.py`: exact z3 model (lane-pair balance + cap on meetings). It proves
  the least `max_meet` for small cases (`results/exact*.json`), and its
  solutions are polished by the anneal and kept when better.
* `repair.py`: tries to re-seat the groups of an unconstrained draw onto pairs
  in a balanced way (z3). It found the zero-repeat groupings of 3×3, 4×4, 5×5
  and 6×4 B=6 cannot be balanced.
* `constructions.py`: GF(q) resolvable transversal designs (q = 3, 4, 5, 7, 8,
  9). They have M rounds with no repeats for any K ≤ M, and are balanced for
  K < M.
* `baselines.py`: NZ rule, move-pairs, single-lane and NZ-without-wrap, all
  scored (`results/baselines.json`).
* `build_schemes.py` writes `schemes.json` (the recommended scheme for every
  (M, K, B) with explicit draw, rule parameters if it is a rule, score, lower
  bounds and the NZ score). `report.py` writes the tables above
  (`results/tables.md`).
* `verify.py` re-scores every scheme in `schemes.json` from its draw alone,
  checks rule draws against the rule, and checks the stored bounds.

`schemes.json` conventions: bowlers are numbered 1..MK by their block-1 seat
((pair − 1)·K + position), and pairs are numbered 1..M.
`draw[block][pair]` lists the bowlers in bowling order. A rule
`{d, pi}` means the bowler in (pair p, position t) moves to
(pair p + d[t] mod M, position pi[t]), with 0-based t and pi.

## Reproducing

```sh
cc -O2 -o rulesearch rulesearch.c && cc -O2 -o anneal anneal.c -lm
for K in 2 3 4 5; do for M in 3 4 5 6 7 8 9 10; do ./rulesearch $M $K 12 > results/rules/M${M}_K${K}.jsonl; done; done
python3 baselines.py
python3 optimum.py --from-rule --secs 20      # then --construct, plain, --from-free, --soft
python3 exact.py 3,3,3 4,4,4 ... --timeout 90  # z3 bounds + designs for small / hard cases
python3 build_schemes.py && python3 verify.py && python3 report.py > results/tables.md
```

Sources: CDE Software KB "Lane Assignments" (lane-change methods), IESA bowling
state-finals lane assignments, and Miller–Valkov–Abel arXiv:2507.23376
(social golfer tables).
