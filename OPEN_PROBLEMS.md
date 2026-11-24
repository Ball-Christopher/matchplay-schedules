# Open problems

Each problem below can be read on its own. The common setting:

- *v* bowlers bowl in groups of *k* (3 or 4), one group per lane pair, so there are *n = v/k* lane pairs.
- A **week** is a partition of the bowlers into *n* groups, each assigned to a different lane pair. Two bowlers who share a group that week **meet**.
- A **round** is a list of weeks in which every couple meets exactly λ times. Equivalently, it is a resolvable 2-(*v*, *k*, λ) design, with the weeks as its parallel classes. A round has *r* = λ(*v*−1)/(*k*−1) weeks.
- A round is **lane-exact** if every bowler is on every lane pair ⌊*r/n*⌋ or ⌈*r/n*⌉ times. The literature calls a lane-exact round a *generalized balanced tournament design* (GBTD).
- A set of weeks is **clash-free** if no couple meets twice within it. It is then a resolvable packing.

Status as of 25 November 2026. The evidence for each claim is in [METHODS.md](METHODS.md); section numbers below refer to it. A literature check (section 12) found none of these problems addressed. Results from Astra (four batches, 24–25 November 2026) were checked independently; see [contrib/astra-2026-11-24](contrib/astra-2026-11-24/README.md), [contrib/astra-2026-11-24b](contrib/astra-2026-11-24b/README.md), [contrib/astra-2026-11-24c](contrib/astra-2026-11-24c/README.md) and [contrib/astra-2026-11-25](contrib/astra-2026-11-25/README.md).

---

## 1. Fewest same-pattern repeats for 12 bowlers in fours — settled

**Problem.**
- Take a resolvable 2-(12, 4, 3) design, which has 11 weeks.
- Split the weeks into *b* blocks.
- Within each block, a couple that meets *t* times there contributes *t*−1 **repeats**.
- What is the minimum total number of repeats over all such designs and splits, for *b* = 4 and for *b* = 3?

**Answer: 27 for 4 blocks and 40 for 3 blocks** (Astra, checked here; [contrib/astra-2026-11-24](contrib/astra-2026-11-24/README.md)).
- Morales and Velarde (*J. Combin. Des.* 9 (2001), [doi:10.1002/jcd.1019](https://doi.org/10.1002/jcd.1019)) classified the resolvable 2-(12,4,3) designs: there are exactly five. Krčadinac's S(2,4,37) paper cites the same count.
- Repeated foursomes are impossible. Four bowlers who shared a group twice would have only 6 meetings left among their 6 couples, but they need at least one meeting in each of the other 9 weeks.
- Each of the five designs has a unique resolution. An exhaustive check over every split into 3 or 4 blocks gives these minima:

  | Design | 3 blocks | 4 blocks |
  |---|---:|---:|
  | 1 | 40 | 27 |
  | 2 | 41 | 27 |
  | 3 | 43 | 28 |
  | 4 | 41 | 27 |
  | 5 | 42 | 28 |

- The library's `4w12-oil` (27 repeats) is therefore optimal.
- The proof rests on the published classification. The minima were recomputed here from Astra's five designs.

## 2. Lane-exact resolvable designs with block size 4 and λ = 1

**Problem.** For which *v* ≡ 4 (mod 12) is there a lane-exact resolvable 2-(*v*, 4, 1) design?

- *n* = *v*/4 lane pairs and *r* = (*v*−1)/3 weeks.
- This is a GBTD with k = 4 and λ = 1.

**Known.**
- *v* = 16 is **impossible**. In the affine plane AG(2,4), the 5 lines on one lane pair pairwise intersect, so they form a pencil (all 5 through one point). A short proof is in section 4; it is also implied by a code bound of Chee et al. (2014).
- *v* = 28 **exists**: a Z₉ × 3 ∪ {∞} construction.
- *v* = 40 **exists**: the lines of PG(3,3) with an order-5 Singer subgroup (METHODS section 13).
- **Quadrupling (Astra, checked here).** If a lane-exact design on *m* bowlers has a suitable 4-colouring of each lane's groups, and an orthogonal array OA(6, *m*) exists, then one exists on 4*m* bowlers, and the colouring condition carries over to the result.
  - This gives **28·4^j and 40·4^j for every j ≥ 0**.
  - Verified witnesses: **112, 160, 448 and 640**. Each has every couple once and every bowler on every lane pair once or twice.
  - A separate 16-fold inflation gives the same 448 and 640.
- **52, 64, 76, 100, 124, 136 and 148 exist** (Astra's second batch, checked here). Each witness has every couple once, every bowler on every lane pair once or twice, and balanced positions.
  - 52, 76, 100, 124, 148: four layers of Z_q (q = 13, 19, 25, 31, 37), one developed base week plus slope weeks *h* + *s_j a*.
  - 64: four copies of GF(16), 16 transversal weeks plus the affine plane AG(2,4) in each layer, with one week's lanes permuted to repair the lane counts.
  - 136: four layers of Z_33 plus 4 extra bowlers.
- **Open below 160: only 88.** Astra's 88 search (Z_21 × 4 + 4) found nothing; that is not a proof.
- The literature covers GBTDs with λ ≠ *k*−1 only for *k* = 3.

## 3. Short-season balance

**Problem.**
- For a round, define the **spread** after *W* weeks as the most times any couple has met minus the fewest.
- Find the least achievable value of max over *W* < *r* of the spread, over all rounds and week orders.
- Also find it with the round required to be lane-exact.

**Known.**
- λ = 1 rounds achieve spread 1 throughout.
- 3-way *v* ≡ 0 (mod 6) needs spread 2, by a structural argument. For 3-way 12 that is optimal, proven by z3.
- 4-way 12 needs spread 2 at weeks 3–4 (z3).
- 4-way 20 cannot go beyond 5 weeks clash-free (social golfer 5-4-6 is infeasible), so it needs spread 2. The lane-exact oil designs for 4-way 20, 24 and 32 achieve **2**, but the lane-exact main designs of 20, 24 and 36 sit at 3.
- **4-way 24: 1 or 2.** Astra's necessary condition for spread 1:
  - weeks 1–7 must be clash-free;
  - after week 7, each bowler has exactly two opponents left to meet;
  - week 8 must contain both of them, so inside each week-8 foursome the unmet couples form a 4-cycle.
  - So spread 1 needs a 7-week clash-free packing whose unmet couples form six disjoint 4-cycles. Astra also gives a 6×6-board construction that turns three such packings into a spread-1 round, ignoring lanes.
  - The packing has not been found.
- **Lane-exact 4-way 36 reaches spread 2** (Astra's four-pattern round, problem 6).
- **The main 4-way 20, 24 and 36 files can't reach spread 2 by reordering** (Astra, checked here with a direct z3 model): every order of their weeks has a prefix where one couple has met 3 times and another 0. New weekly groups would be needed; the oil files of the same sizes already reach 2.
  - Astra's cyclic search on the six 4-cycle components found no spread-1 packing for 4-way 24.
  - Local trades from the published packing don't help (Astra, fourth batch; rechecked here). The 7 fours weeks of `hybrid/files/v24_0-1-7.json` leave 8 disjoint unmet triangles. Keeping any 3 of the weeks and refilling the other 4 in every possible way gives exactly 7 other packings, and each is a relabelling of the original. So any chain of trades that change at most 4 weeks at a time keeps the 8 triangles. A spread-1 search has to start from a different packing or change at least 5 weeks at once.
- **Open:** spread 1 for 4-way 24, and a general rule for the least possible spread.

## 4. Oil patterns over two rounds

**Problem.** For the λ > 1 sizes, a two-round schedule has 2*r* weeks and every couple meets 2λ times. What is the fewest clash-free consecutive blocks such a schedule can be split into?

- The two-round files should also stay lane-exact, with round 1 equal to the one-round file.
- Lower bounds (Astra, checked):
  - Greedy cutting (always take the longest clash-free run) is optimal for a fixed order.
  - Let the fixed round 1 cut greedily into *g* blocks, the last of length *t*, and let *L* be the longest possible clash-free run. Then at least *g* − 1 + ⌈(*t* + *r*)/*L*⌉ blocks are needed.

**Known.** Each row keeps round 1 exactly equal to the one-round file, and every upper bound has a lane-exact witness with balanced positions (Astra; checked in the two contrib folders).

| Size | Round 1 = oil file | Round 1 = main file |
|---|---|---|
| 3-way 12 | 6 (4+3+4+3+4+4), optimal | — |
| 3-way 18 | **5** (8+5+6+7+8), optimal | **6**, optimal |
| 3-way 24 | **5** (11+6+8+10+11), optimal | **18**, optimal |
| 3-way 30 | **5**, optimal | **18**, optimal |
| 3-way 36 | **5** (16+10+12+16+16), optimal | **24**, optimal |
| 4-way 20 | **8**, optimal | **19**, optimal |
| 4-way 24 | **8**, optimal | **16**, optimal |
| 4-way 32 | **8**, optimal | **8**, optimal |
| 4-way 36 | 7–8 (with the new 4-pattern oil round) | 29–30 |

- **Proofs beyond the simple bound.**
  - 4-way 24 main: the groups that avoid every couple in round 1's last block (5 weeks) contain no complete week, so that block can't be extended at all. That forces 12 + ⌈23/7⌉ = 16.
  - 4-way 32 (either round 1): only 7 groups avoid round 1's last 8-week block, and a week needs 8, so the cut is forced. That gives 4 + ⌈31/10⌉ = 8.
- **3-way 36 oil (Astra, third batch):** round 2 is three 12-bowler layers plus two transversal systems, and its first 3 weeks join round 1's 9-week tail, giving 16+10+12+16+16.
- **4-way 36 main:** 29 would need Astra's 4-pattern round to put its 8-week class straight after round 1's last 3-week block. That is impossible for any relabelling (checked here: the couples that class leaves free form 4 disjoint K9s plus 9 disjoint K4s, and no 3 clash-free weeks fit inside them). A different round 2 could still reach 29.
- **3-way 24 (Astra, fourth batch):** round 2 is three clash-free parts of 2, 10 and 11 weeks. The 11 weeks are a nearly Kirkman triple system, made by doubling a 12-point design. The 10 weeks have an order-3 symmetry, and the 2 opening weeks are rebuilt from their unmet couples. Those 2 weeks join round 1's tail, giving 11+6+8+10+11 after the oil round and 4, fourteen single weeks, 7, 10, 11 after the main round. Both meet the bound.
- Open: 4-way 36 only (7–8 oil, 29–30 main).

## 5. Rotating the short group in vacancy schedules — settled

**Problem.** In an N−1 bowler schedule, one group each week is a bowler short. Can the empty slot be spread evenly over the lane pairs while every real bowler stays lane-exact?

**Answer: yes, exactly when a lane-exact full-roster round exists** (Astra, checked here).
- Take any bowler of a lane-exact full round as the empty slot. It then visits every lane pair ⌊*r/n*⌋ or ⌈*r/n*⌉ times.
- Conversely, put a dummy in the empty slot. A real bowler who meets every other real bowler λ times also meets the dummy λ times, by counting opponent slots. So the dummy's schedule is a full lane-exact round.
- That is impossible for full rosters of 15 in trios and 12 or 16 in fours, so 14 in trios and 11 or 15 in fours cannot have both.
- Astra's verified tables: 11, 17, 20, 23 and 26 in trios; 19, 23, 27 and 39 in fours.
- **Library:** the vacancy files now rotate the slot this way wherever possible (`tools/rotate_vacancy.py`). The remaining fixed-slot cases are 14 in trios and 11 or 15 in fours, where it can't be done.

## 6. Four oil patterns for 36 bowlers in fours — settled

**Problem.** Is there a resolvable 2-(36, 4, 3) design (35 weeks) whose weeks split into 4 clash-free sets? A clash-free set has at most 11 weeks, so the sizes would be close to 9+9+9+8.

**Answer: yes** (Astra's second batch, checked here). The witness is 9+9+9+8, with all 35 weeks distinct, exact lanes (3 or 4 visits per lane pair), balanced positions and prefix spread 2. Four is optimal, because 3 × 11 < 35.
- Construction: four layers of GF(9) = GF(3)[*i*]. The three Hamilton cycles on the four layers give three 9-week patterns. Each base week holds the four layer zeros, plus, on each directed cycle edge, ±1 with ±(1+*i*) and ±*i* with ±(2+*i*). The last 8 weeks are transversal weeks *h* + *s_j a* with coefficients 0, 1, 2, *i*.
- The earlier Z_9 × 4 template is impossible (no (9,4;1) difference matrix over Z_9). The library's current file has 11 sets.

## 7. Qualifying movements: mixing under lane-pair balance

**Problem.**
- M lane pairs with K bowlers each bowl B blocks.
- Every bowler must be on every pair ⌊B/M⌋ or ⌈B/M⌉ times.
- Minimise the most times any couple shares a pair, then the most times any bowler follows the same bowler on the same lane.

**Known.** Full tables are in [qualifying/README.md](qualifying/README.md).
- With no balance condition and no couple meeting twice, this is the social golfer problem.
- Pair balance sometimes costs mixing. z3 proves this for 3×3, 3×4, 3×5, 4×4, 4×5 and 5×5.
- **Astra's second batch** (checked; [contrib/astra-2026-11-24b](contrib/astra-2026-11-24b/README.md)) has 33 draws for B ≤ 12. 32 of them are proven optimal on both max meetings and max follows, either by counting or by the arguments below. 24 improve on the published draw. The new lower bounds:
  - 6×4 at B = 6: the lane words would be a permutation array of length 6 and distance 5 with 24 words, but the maximum is 18.
  - 6×5 at B = 4–6: one meeting would give two orthogonal Latin squares of order 6.
  - 5×3 at B = 7: one meeting would give a KTS(15), and none of the seven has balanced lanes.
  - 4×3 at B = 6 needs 2 by plain counting (12 opponent slots, 11 opponents). This list wrongly had it as open.
  - 3×4 at B = 7 needs 3, and at B = 11 needs 4 (no GBTD(4,3)).
  - 3×3 at B = 3 needs 2 follows: two bowlers share all three pairs and must repeat a follow direction.
- **3×4 at B = 11 is now optimal on all ten fields** (Astra, third batch): 4 meetings, every ordered follow exactly once.
- **5×3 at B = 6 needs 2 meetings** (Astra, fourth batch; rechecked here by an independent exhaustive search, [contrib/astra-2026-11-25](contrib/astra-2026-11-25/README.md)). A one-meeting draw would be 15 lane words of length 6, each with one lane twice, agreeing in at most one place and filling every block's lanes with 3 bowlers. There are none. The published draw (2 meetings, 1 follow) is optimal on both.
- **Open:** the cases outside Astra's tables.
- **Library:** the new draws are in `qualifying/schemes.json` wherever they score better (`qualifying/results/astra/`).

---

## Settled since the library was built

- **Fewest repeats for 12 in fours: 27 (4 blocks), 40 (3 blocks)** (problem 1).
- **Rotating vacancy: possible exactly when a lane-exact full round exists** (problem 5).
- **Lane-exact one-meeting fours at 28·4^j and 40·4^j**, including 112, 160, 448 and 640 (problem 2).
- **Two-round oil: 4-way 20 reaches 8, optimal**; 3-way 18 reaches 5, optimal (problem 4).
- **Four oil patterns for 24 bowlers in fours: yes**, as 6+5+6+6, lane-exact and with prefix spread 2 (METHODS section 13). Four is optimal: a clash-free set has at most 7 weeks, and 3 × 7 < 23. The design uses 6 super-points × Z₂² with an order-3 map cycling three blocks. Astra found an independent 6+6+6+5 design from an S₄ action; its lanes are not exact.
- **Lane-exact 4-way 40 exists** (problem 2).
- **Lane-exact one-meeting fours at 52, 64, 76, 100, 124, 136, 148**; below 160 only 88 is open (problem 2).
- **Four oil patterns for 36 in fours: yes**, 9+9+9+8, lane-exact, spread 2 (problem 6).
- **Two-round oil, fixed round 1:** 4-way 24 (8 oil, 16 main), 4-way 32 (8, 8), 3-way 30 (5, 18) and 3-way 36 main (24) are optimal (problem 4).
- **Two-round oil for 3-way 36: 5 patterns, optimal** (problem 4).
- **Two-round oil for 3-way 24: 5 (oil first) and 18 (main first), both optimal** (problem 4).
- **Qualifying 5×3 at B = 6 needs 2 meetings**, so the published draw is optimal on meetings and follows (problem 7).
- **Qualifying:** all of Astra's 33 draws are now proven optimal on meetings and follows (3×4 at B = 11 closed in the third batch). 6×4 at B = 6 and 6×5 at B = 4–6 are proven to need 2 meetings (problem 7).

- **4-way 12, lane-exact, is impossible.** No GBTD(4,3) exists: Chee, Kiah and Wang, *Electron. J. Combin.* 20(2) (2013) #P51. So 1 bowler off is the best possible.
- **3-way 15, lane-exact, is impossible.** We checked all 7 KTS(15); this agrees with Chee, Kiah, Ling and Wang, *J. Combin. Des.* 22 (2014).
- **4-way 16, lane-exact, is impossible** (problem 2).
