# How the schedules were found

This records how each schedule was built, what was tried, what failed and why, and what is proven impossible. It was written on 21 November 2026, when the library was built. Every file can be re-checked from its weeks alone with `python3 verify.py`. Each JSON also has a short `method` field.

**Limitations at a glance**

- **Lane pairs not exact in three single rounds, all proven best possible or impossible to improve:** 3-way 15 (1 bowler off), 4-way 12 (1 off) and 4-way 16 (12 off; 3 off in the vacancy version). The two-round versions of all three are exact.
- **Oil patterns:** 4-way 12 can't avoid couples meeting twice on a pattern (27 extra meetings, proven minimal; section 14). 4-way 36 now uses 4 patterns, the fewest possible (Astra, section 14).
- **Short seasons:** a season stopped part-way through a long schedule is less even than a full one; see section 8 and each schedule's "stopping early" figure.
- **Vacancy files:** the short group moves round the lane pairs evenly wherever a lane-exact full round exists. Only 3-way 14 and 4-way 11 and 15 can't have this (section 14).
- **Two-round files:** a few groups from round 1 meet again in round 2 (3-way 12, 18 and 24, and 4-way 12).

## 1. The problem

There are v bowlers in groups of k (3 or 4), with one group per lane pair, so n = v/k lane pairs. A schedule is r weeks long. Each week is a permutation of the roster, read in groups. Three things are balanced, in priority order:

1. **Couples.** Every couple of bowlers shares a group exactly λ times. This makes the schedule a *resolvable 2-(v,k,λ) design*: each week is a "parallel class" and each group a "block". It needs r = λ(v−1)/(k−1) weeks, so λ is the smallest value that makes r a whole number.
2. **Lane pairs.** Every bowler is on every lane pair ⌊r/n⌋ or ⌈r/n⌉ times. This depends only on the order of the groups within each week.
3. **Positions.** Every bowler holds each position ⌊r/k⌋ or ⌈r/k⌉ times. The positions are left 1st, right 1st, left 2nd, and right 2nd for 4-way. This depends only on the order within each group.

The three axes are separable: changing one doesn't disturb the others. Lane balance turned out to be the hard one.

| k | v | λ | weeks r | why that λ |
|---|---|---|---|---|
| 3 | 15, 21, 27 | 1 | 7, 10, 13 | v ≡ 3 (mod 6): Kirkman triple systems |
| 3 | 12, 18, 24 | 2 | 11, 17, 23 | v ≡ 0 (mod 6): λ = 1 would need (v−1)/2 weeks, not a whole number |
| 4 | 16, 28 | 1 | 5, 9 | v ≡ 4 (mod 12): affine plane, resolvable (28,4,1) |
| 4 | 12, 20, 24 | 3 | 11, 19, 23 | v−1 isn't divisible by 3, so λ = 3 |

## 2. Pair balance: constructing the designs

Pair balance was never the bottleneck. Every case gave way to one of the following.

- **Extended circle method (1-rotational).** Points are Z_(v−1) ∪ {∞}. A *base week* is searched for whose groups' differences (x − y mod v−1, over pairs not involving ∞) cover every non-zero residue exactly λ times. Developing the base week (adding 1, 2, … mod v−1) then gives v−1 weeks with perfect pair balance.
  - For 4-way 20, random local search on the difference counts found a base week in under a second, for example `[[1,10,9,∞],[16,17,3,6],[11,14,18,4],[0,13,15,2],[12,5,7,8]]`. 4-way 12 and 24 and 3-way 12, 18 and 24 were built the same way.
- **Kirkman triple systems (3-way 15, 21, 27).** These use points Z_m × {classes} ∪ {∞}, with one or two base weeks developed mod m, found by randomised backtracking on difference counts: Z_7 × 2 for 15, Z_5 × 4 for 21 and Z_13 × 2 for 27.
- **4-way 16:** the affine plane AG(2,4), whose lines over GF(4)² fall into 5 parallel classes.
- **4-way 28:** Z_9 × 3 classes ∪ {∞}, developed mod 9. Developing over Z_27 would give 27 weeks, not 9.
- **Direct SAT (z3).** For 3-way 12 and 4-way 12, z3 built the whole design at once, with the short-season (prefix) constraints included.

## 3. Lane balance: what was tried

### 3.1 The circle method nearly does it
In a 1-rotational design, keep base group j on lane pair j every week. A finite point x sits in base group j in exactly as many weeks as that group has finite points. So every finite bowler's lane counts come out exact automatically, for example 4,4,4,4,3 for 4-way 20.

The exception is **∞**, which sits in the same base group every week and so is stuck on one lane pair for the whole round. This is the same as the classic round-robin circle method, and it's why the first `_vacant` files worked: make ∞ the empty slot (section 5). The current files rotate the slot instead.

### 3.2 Fixing ∞ by reordering lanes (4-way 20, one design)
Each of these failed:

| Attempt | Result |
|---|---|
| Simulated annealing over within-week group order | stalled with 6 of 20 bowlers one off |
| Rotating rule lane = (block + c·week) mod 5, over all permutations, step sizes c and multipliers of Z_19 | best had 16 bowlers off |
| z3 pseudo-boolean model of the full lane problem | no answer in 5 minutes |
| z3 with only the ∞ group's lane swapped, one swap per week | **unsat**: swapping alone can't fix it |
| GLPK MILP, 475 binaries | nothing found in 23 minutes; not proven infeasible either |
| Annealing across 263 different base designs | best: 5 bowlers with one lane pair 5 times |
| Fable agent: a faster C annealer on the original base, about 900 restarts | best: 2 bowler-lane cells off |

The agent's rough count suggested exact lane orders probably do exist for that design but are far too sparse to find by local search. No impossibility was shown.

### 3.3 The breakthrough: designs whose symmetry also rotates the lanes
This was found by a Fable agent and then reused for every hard case. Instead of fixing a design and then hunting for lane orders, it builds a design with a symmetry group that acts on the lane pairs too.

- **4-way 20:**
  - Points Z_5 × {0,1,2,3}, with the map i → i+1 also moving every group up one lane pair.
  - 3 base weeks, each developed into 5 weeks, give 15 weeks. 4 more weeks are each fixed by the symmetry: one group with one bowler from each class, developed mod 5.
  - Pair balance becomes a small difference-family condition (38 difference types, each covered 3 times). Annealing in C solved it in about a minute.
  - Lane counts then depend only on (lane − i) for each class. That leaves 120³ base-week lane permutations × 5⁴ offsets for the fixed weeks, a space an exhaustive search covers instantly. The first valid design worked.
- **4-way 24:**
  - The group Z₂² × Z₃ acts on two orbits of bowlers. Z₃ rotates the lane pairs within two tracks of three, and Z₂² leaves the lanes fixed.
  - The 23 weeks are one free week × 12, two Z₃-invariant weeks × 4 and one coset week × 3.
  - The agent's first exact version repeated the same six foursomes in weeks 1, 12 and 22. The library uses its alternative, which has 23 distinct weeks. Its prefix spread is 3 rather than 2.
- **3-way 24:** points Z_8 × 3 classes, with the 8 lane pairs rotated. Two base weeks developed mod 8 give 16 weeks, plus 7 Z_8-invariant weeks. A DFS on the (lane − x) residues found the lanes in 0.02 s.
- **3-way 27:** two different KTS(27) on Z_9 × 3, rotating the 9 lane pairs. Each is one base week developed mod 9 plus 4 invariant weeks, and each is exactly lane-balanced on its own.

**Dead ends within this approach:**
- **4-way 24 with a single order-6 rotation** (Z_6 × 4) is impossible. Antipodal pairs are covered an even number of times, so λ = 3 can't be reached.
- **4-way 12 with Z₂² × Z₃** can't work. 11 weeks is fewer than the 12 needed to cover pairs in the same Z₃ orbit.
- **4-way 12 with Z₃ and fixed points** would need 3 to divide 11.

## 4. Impossibility results and unresolved cases

| Case | Status | Argument |
|---|---|---|
| 4-way 16, single round | **impossible** | A lane pair gets one line from each of the 5 parallel classes, and any two of those lines meet. For the 5 lines to cover all 16 bowlers, the only possibility is all 5 passing through one point (a "pencil"), which puts that bowler on the lane pair 5 times. Two pencils always share a line, so the lane pairs can't all be pencils. The same argument rules out the vacancy version, which is 3 bowlers off at best. |
| 3-way 15, single round | **impossible** | Exhaustive exact-cover enumeration, with the first week and one trio fixed without loss of generality, gives 224,640 KTS(15). Isomorphism testing reduces these to exactly 7 systems (\|Aut\| = 168, 168, 24, 24, 12, 12, 21), and orbit–stabiliser sums back to 224,640. For each of the 7, z3 says unsat in 0.03 s, and an independent DFS of about 11M nodes finds nothing. Lane balance doesn't change under isomorphism, so this covers every KTS(15). |
| 4-way 12, single round | **impossible** (literature) | Our search: 236 annealed designs, each checked exhaustively for a lane order (`lanes.c`), were all infeasible, as were the original z3 design and 60 cyclic Z_11 designs; about 480 joint anneals reached 1 off 59 times and never 0. The literature settles it: this is a generalized balanced tournament design GBTD(4,3), which Chee, Kiah and Wang (2013) prove does not exist (no ternary equitable-symbol-weight code of length 11, distance 8 and size 12; the maximum is 11). So 1 bowler off is the best possible. |

## 5. Vacancy (n−1) files

**Current files (24 November 2026).** 3-way 12, 18, 24, 27, 30 and 36 and 4-way 20, 24, 32 and 36 are built by `tools/rotate_vacancy.py`. The tool takes the lane-exact main round and makes one bowler the empty slot. That bowler is chosen for the smallest prefix spread and renumbered to N.
- The slot then visits each lane pair ⌊r/n⌋ or ⌈r/n⌉ times.
- The real bowlers keep the main round's exact lanes, positions and pair counts.
- This is possible exactly when a lane-exact full round exists (section 14).

The earlier versions are described below. In them, the ∞ point was the empty slot, so every real bowler was lane-balanced (section 3.1).
- **3-way 12, 18 and 24, and 4-way 20 and 24 (replaced):** the 1-rotational design with base group j on lane pair j. The short group was always on the same lane pair.
- **4-way 12:** the circle-method version was also exact, but the z3 design (lanes re-solved for the 11 real bowlers) has a better prefix, so that was used.
- **4-way 28:** the 9-week design is already exact, so any slot can be left empty.
- **3-way 15 and 21:** an exhaustive search found **no 1-rotational KTS** under Z_14 or Z_20. These use the main KTS with lanes re-annealed for the real bowlers, and are exact.
- **3-way 27:** a 1-rotational KTS over Z_26 exists (its base week is fixed by +13), but a KTS is developed over only half the group, so fixed lanes don't balance it. Lanes were annealed instead, and are exact.
- **4-way 16:** AG(2,4) in 1-rotational form (GF(16), x → g³x) has base lines whose orbit compositions include zeros, so fixed lanes don't work either. The best is 3 bowlers off, and section 4 shows exact is impossible.

## 6. Two-round files

Round 2 keeps every couple's count right under any relabelling of the bowlers, so the work goes into lanes and variety.

- **Method 1: relabel and shift.** Used for 4-way 20 and 24, where round 1 is lane-exact with one short lane pair per bowler. Round 2 is round 1 with every group moved up one lane pair, plus a bowler relabelling chosen so nobody's short lane pair lines up with their short pair from round 1. That gives totals of exactly ⌊2r/n⌋ or ⌈2r/n⌉. A random search over relabellings also avoids repeating groups from round 1.
- **Method 2: relabel by matching** (`tools/schedlib.py: second_round`). This uses a random lane permutation, and then bipartite matching assigns a new label to each bowler so that every bowler's totals over both rounds are in range. It was used for 3-way 12, 15, 18, 21 and 24, keeping the round that repeats the fewest groups out of up to 4,000 tries. It replaced the 3-way agent's first versions, cutting repeated trios from 8/2/16/3/21 to 1/0/3/0/4. 3-way 15 works even though its single round isn't exact, because round 2 makes up the shortfall.
- **4-way 12, 16 and 28:** the 4-way agent's version (`build.py: relabel_cycle`), a relabelling by bipartite matching plus a lane permutation. These are exact with 2/0/0 repeated groups.
- **3-way 27:** Method 2 found nothing in 20,000 tries, because round 1 has four doubled lane pairs per bowler. The agent's freer annealing of round 2's lane order, with a Hungarian-optimal relabelling at every step, stalled at 3–5 cells off after 34 runs. The fix was the Fable agent's **pair of KTS(27)s** built together (section 3.3), each exact alone and exact together with no repeated trios. Its first round replaced the original `v27.json`.

- **Astra's two-round files (24 November 2026, section 14):** round 1 is copied row for row, and round 2 is relabelled so each bowler's less-frequent lane pair and position differ from round 1's. Where possible a short colour class of round 2 is joined to round 1's last block. They replaced `v24_x2`, `v30_x2` and `v36_x2` (3-way) and `v24_x2` and `v36_x2` (4-way), which needed 29/34/40 and 24/52 oil-pattern blocks; the replacements need 19/18/24 and 16/30. They also supplied `v24_oil_x2`, `v30_oil_x2`, `v36_oil_x2` (3-way) and `v24_oil_x2`, `v32_oil_x2` (4-way).
- **3-way 24, fourth batch (25 November 2026, section 14):** Astra's new round 2 replaced `v24_x2` (19 blocks, now 18) and `v24_oil_x2` (6, now 5). Both are optimal. Imported by `tools/import_astra_b4.py`.
- **4-way 36 oil, two rounds** (`tools/import_astra_b2.py`): Method 2 with positions added to the matching, on the new 4-pattern round. 8 blocks; the lower bound is 7.

**Left as is:** a few groups recur across the rounds in 3-way 12 (1), 3-way 18 (3) and 4-way 12 (2). These designs have every couple meeting at least twice per round, which leaves little room. Astra's optimal 3-way 24 files repeat more: 22 of round 2's 184 trios in `v24_x2` and 23 in `v24_oil_x2` also occur in round 1 (the files they replaced had 9 and 8). That is the price of the fewer oil-pattern blocks so far; a relabelling search that keeps the blocks might lower it.

## 7. Positions

This is an equitable edge-colouring of a bipartite graph, which always exists (de Werra). Each bowler's appearances are split, in week order, into consecutive chunks of k, and each chunk becomes a vertex. Edges join each (week, group) to those vertices. The resulting graph has maximum degree k, so König's alternating-path method gives a proper k-colouring, and the colour is the position.

Because the chunks are consecutive, every bowler stays within one of an even share after every week, and not just at the end. This is exact for every file (`tools/positions.py`).

## 8. Short seasons (prefix spread)

`prefix_spread[W]` is the max − min of couple meetings after W weeks. The week order (which never affects lanes or positions) was annealed to keep it small. Some limits are structural:

- **20 bowlers in fours** can go at most 5 weeks with no couple meeting twice (the social golfer problem), so spread ≥ 2 soon after that. 4-way 20 and 24 peak at 3 around mid-season.
- **3-way v ≡ 0 (mod 6):** spread 2 can't be avoided. Spread ≤ 1 at week (v−2)/2 forces those weeks to be couple-disjoint, and the unmet couples then can't fit into one week. For 3-way 12, z3 proved "weeks 1–4 disjoint and everyone met by week 6" unsatisfiable, so two weeks at spread 2 is optimal.
- **4-way 12:** any two weeks share a couple by pigeonhole, and z3 proves spread 1 impossible at weeks 3 and 4.
- **λ = 1 designs (15, 21, 27, 16, 28):** spread 1 throughout.

A league that will only run part of a long design, for example 8 weeks of the 19-week 4-way 20, would do better with a purpose-built short design than with the first weeks of a full one.

## 9. Who did what, and the compute used

| Work | By | Rough compute |
|---|---|---|
| 4-way 20 circle design, lane attempts in section 3.2, positions method, vacancy and two-round files for 20 | main session | about 40 min of solver time (z3, GLPK, annealing) |
| 3-way library: KTS and 1-rotational designs, vacancy, first two-round versions | 3-way agent | about 80 min |
| 4-way 12/16/24/28 library, AG(2,4) impossibility, vacancy, two-round | 4-way agent | about 50 min |
| Exact 4-way 20 (Z_5 × 4) | Fable agent | about 9 min |
| Exact 4-way 24, 4-way 12 search | Fable agent | about 30 min |
| Exact 3-way 24 and 27 pair, KTS(15) impossibility | Fable agent | about 30 min |

**Code:**
- `tools/` (shared): `positions.py` for position assignment and `schedlib.py` for week ordering, standard output and the two-round builder.
- `3way/tools/`: `gen.py` and `prefix_sat.py` from the agent, plus `fable_search/`, which holds the Z_8 and Z_9 searches and the KTS(15) proof (`k15*.c`, `iso15.py`).
- `4way/tools/`: the agent's `build.py` and helpers, `v20_z5_search.c`, and `v12_v24_fable_search/`.

The agents' own `verify.py` scripts are kept in their tools folders. The 3-way one expects fields from its first versions, so use the top-level `verify.py`.

## 10. Oil-pattern blocks

This section was added on 21 November 2026.

**The target.** Split a round into contiguous blocks, one oil pattern each, so that no couple meets twice within a block. Use as few blocks as possible, with any block lengths. A clash-free block is a *resolvable packing*, so the lower bound is ⌈r / (longest possible clash-free run)⌉:

| Size | Longest clash-free run | Source | Lower bound |
|---|---|---|---|
| 3-way 12 | 4 | NKTS(12) doesn't exist (known); z3 was inconclusive at 5 weeks in 150 s | 3 |
| 3-way 18 / 24 | 8 / 11 | NKTS(v) exists for v ≡ 0 (mod 6), v ≥ 18 | 3 / 3 |
| 4-way 12 | **1** | any two weeks share a couple: a week-2 foursome holds ≤ 1 bowler from each of the 3 week-1 foursomes | n/a, repeats are unavoidable |
| 4-way 20 | 5 | social golfer 5-4-6 is infeasible (known); z3 found 5 weeks and was inconclusive at 6 | 4 |
| 4-way 24 | 7 | social golfer 6-4-7 is solvable (a 4-RGDD of type 3^8; Miller, Valkov and Abel 2025) and 7 is the counting bound | 4 |

The λ = 1 designs are trivial: one round is one pattern. Their two-round files give two patterns, one per round, so each couple meets once on each. This holds as ordered.

**Measuring the existing designs.** Find the chromatic number of the graph whose vertices are weeks, with an edge whenever two weeks share a couple. Exact backtracking gave:

| Design | Blocks needed |
|---|---|
| 3-way 12 | 3 |
| 3-way 18 | 4 |
| 3-way 24 | 9 |
| 4-way 12 | 11 (the graph is complete) |
| 4-way 20 | 12 |
| 4-way 24 | 10 |

Lane-rotating symmetric designs, good for lanes, are poor for blocks because their repeats sit close together.

**Results**

- **3-way 12:** already optimal. Weeks 1–4, 5–7 and 8–11 as ordered give 0 repeats, found by exhaustive search over 4/4/3 splits.
- **3-way 18: [8, 5, 4], exact lanes.**
  - Block 1 is an NKTS(18) missing a 1-factor F.
  - Blocks 2 and 3 form a resolvable 9-week covering whose doubled pairs are exactly F, split 5/4 so each F pair falls once on each side.
  - Both parts were found by z3 with an imposed order-3 automorphism, then relabelled to share F. z3 also solved the lanes.
  - **Ruled out:** cyclic Z_17 ∪ {∞} designs can't give 3 blocks (exhaustive search), and the 8 + 8 + 1 split is impossible: the two missed 1-factors join into even cycles, which have no triangles.
- **3-way 24: [11, 6, 6], exact lanes.** This is the file's current version, from a second Fable pass.
  - A Z_8 × 3 lane-rotating design: two base weeks A0 and B0 developed mod 8, plus 7 invariant weeks.
  - B0 uses 24 distinct pair-orbits, so its 8 weeks are clash-free. Block 1 is those 8 weeks plus 3 invariant weeks: an NKTS(24) that leaves out the antipodal pairs.
  - A0 holds the three antipodal {i, i+4} triples, so A_i clashes only with A_(i+4). Block 2 is A0–3 plus 2 invariant weeks, and block 3 is A4–7 plus 2.
  - A0 and B0 were found by backtracking over pair-orbit capacities in about 90 s. Variants with fewer than 3 invariant weeks in the B block have no solution.
  - Lanes reduce to 3 multisets of residues, solved instantly. The worst prefix spread is 2, in weeks 12–14 only.
  - Code: `3way/tools/oil_search/v24_exact/`.
- *First pass, superseded: [8, 8, 7], with 4 bowlers off on lanes.*
  - A cyclic design over Z_23 ∪ {∞} with base week {0,6,21} {1,13,∞} {2,7,15} {3,12,17} {4,14,20} {5,9,16} {8,10,11} {18,19,22}. Every repeat falls 8–15 weeks apart, so weeks 0–7, 8–15 and 16–22 are clash-free.
  - Annealing stalls at 4 lane violations, and z3 timed out after 15 minutes.
  - A Z_8 lane-rotating 3-block design was tried (8 configurations, 7 minutes each in z3) with no answer. That's the most promising route to exact lanes.
- **4-way 20: [5, 4, 5, 5], exact lanes, prefix spread 2.**
  - A new Z_5 × 4 design in which each base week's Z_5 orbit is a clash-free 5-week block, and the 4 invariant weeks form the fourth block.
  - Found by annealing on difference types with a within-block penalty, then the exhaustive rotating-lane search.
  - This design is also better for short seasons than the main v20 (worst prefix spread 2 against 3).
- **4-way 24: now [6, 5, 6, 6], exact lanes (third pass, below). The first two passes reached only 8 blocks:**
  - The file is a lane-exact Z₂² × Z₃ design split by exact colouring. Only 20 of its 23 weeks are distinct.
  - **Failed routes to 4 blocks:**
    - Z_5 on 20 points with 4 fixed points is impossible by counting: at most 16 of the 24 pure-difference slots can be filled.
    - Z₃ × 8 classes never reached pair balance even without blocks (best defect 8–10). An obstruction is suspected but unproven.
    - Z₂² × Z₃ with free week colouring stayed far from feasible for 4 to 7 blocks.
  - **Second Fable pass** (code in `4way/tools/oil_search/v24_4block_attempts/`):
    - **1-rotational Z_23 ∪ {∞}: impossible**, for any assignment of developed weeks to 4 blocks, contiguous or not. A couple's meeting weeks differ by the base-week offsets, so the weeks must properly 4-colour a circulant graph on Z_23. Up to multipliers only 2 maximal 4-colourable connection sets exist, one of them the 6/6/6/5 arcs. An exhaustive DFS over base weeks finds 0 solutions for both, while the same DFS without blocks finds tens of thousands of designs.
    - **(Z_5 ∪ ∞) × H with H = Z_4 or Z₂² cycling the 4 blocks: impossible** by exhaustive DFS.
    - **Inconclusive:** the same with only H imposed (annealing stalled at cost 22–32); z3 with a free resolution (12 difference families).
    - **No counting obstruction:** each couple skips one block, and 5+5+5+8 = 23 per bowler. So 4 blocks remains open for non-symmetric designs.
    - **Not tried:** unsymmetric joint annealing, Z_3 cycling three 6-week blocks, and starting from a 7-week 4-RGDD of type 3^8 (known to exist) as the first block.
    - **Literature:** nothing found on splitting a resolvable design into resolvable packings this way (section 12).
- **4-way 12: repeats can't be avoided.**
  - The figure measured is the sum over couples and blocks of (meetings in the block − 1).
  - With the library v12, the best 4-block split (2,3,3,3) gives 27, and the best 3-block split gives 41.
  - Across 237 designs, 27 remains the best for 4 blocks, and 40 is the best for 3 blocks.
  - z3 didn't settle ≤ 26 (4 blocks) or ≤ 40 (3 blocks) in about 20 minutes.
  - In the file, 42 couples meet on 3 patterns, 21 on 2 and 3 on 1.

- **4-way 36: [9, 9, 9, 8], exact lanes, prefix spread 2** (Astra, section 14). Four layers of GF(9); each Hamilton cycle of K_4 on the layers gives a 9-week pattern, and 8 transversal weeks finish the round. It replaced the 11-block Z_9 × 4 file.

The search code is in `3way/tools/oil_search/` and `4way/tools/oil_search/`.

## 11. Still open

- ~~A proof for exact lane balance in the 4-way 12 single round.~~ Settled: impossible, by a published result (section 12).
- Prefix-optimal ordering searched jointly with lane exactness. At present prefix order is tuned only after lanes are fixed, and 4-way 20 and 24 sit at 3.
- ~~Oil-pattern blocks: 4 blocks for 4-way 36, a proof of the best possible for 4-way 12, two-round oil versions of the λ > 1 sizes.~~ 4-way 36 and 4-way 12 are settled (section 14). Two-round oil files now exist for every λ > 1 size; the gaps left are in OPEN_PROBLEMS.md problem 4.

## 12. What the literature says

A literature check on 21 November 2026 found that lane balance is an established topic: a lane-balanced resolvable design is a **generalized balanced tournament design** (GBTD, or GBTP for packings), with the lane pairs as the rows of an array whose columns are the weeks. Such designs are equivalent to optimal *equitable symbol weight codes*, which is how the small cases were settled by computer.

| Question | Status | What is known |
|---|---|---|
| 3-way, λ = 1 (Kirkman), lane-exact | **Solved** | Exists for 3m bowlers exactly when m is odd and m ∉ {3, 5}. So 21 and 27 exist and **15 is impossible**, agreeing with our exhaustive check of all 7 KTS(15). [1] |
| 3-way, λ = 2, lane-exact | **Solved** | Exists for every 3m except m = 2, so 12, 18 and 24 exist, as found. [3] |
| 4-way, λ = 3, lane-exact | **Solved** | Exists exactly when m = 1 or m ≥ 4 (m = lane pairs). So 20 and 24 exist, and **12 (m = 3) is impossible**. [2, 4] |
| 4-way 16, λ = 1 (AG(2,4)), lane-exact | **Known impossible** | Shown by an exhaustive code search (at most 12 codewords, not 16). Our pencil argument (section 4) is a short proof; we did not find it published. [1] |
| 4-way 28 and 40, λ = 1, lane-exact | **Apparently new** | GBTDs with λ ≠ k−1 had been studied only for block size 3; we found no result for block size 4 with λ = 1. Both exist (sections 3.3 and 13). |
| Social golfer 5-4-w and 6-4-w | **Solved** | 20 golfers: at most 5 weeks. 24 golfers: 7 weeks, which is optimal. NKTS(v) exists exactly for v ≡ 0 (mod 6), v ∉ {6, 12}. [5, 6] |
| 4 oil patterns for 4-way 24 | **Not addressed** | No work found on partitioning a resolvable design's weeks into resolvable packings with each couple missing exactly one block. Nestings and partitioned GBTDs are different conditions. Still open. |
| Fewest same-pattern repeats for 4-way 12 | **Not addressed** | CSPLib's social golfer page names a "fewest repeats" variant but gives no results. Still open. |
| Short-season (prefix) balance | **Not addressed** | Nothing found under this framing. |
| Bowling and sailing leagues | **Partly known** | Sailing league scheduling has been treated with resolvable designs and coverings [7]; an informal bowling note uses precomputed tables [8]. Position balance has an analogue in whist tournaments. |

**References**

1. Y. M. Chee, H. M. Kiah, A. C. H. Ling, C. Wang, "Generalized balanced tournament packings and optimal equitable symbol weight codes for power line communications", *J. Combin. Des.* 22 (2014). [doi:10.1002/jcd.21398](https://doi.org/10.1002/jcd.21398), [arXiv:1304.0278](https://arxiv.org/abs/1304.0278).
2. Y. M. Chee, H. M. Kiah, C. Wang, "Generalized balanced tournament designs with block size four", *Electron. J. Combin.* 20(2) (2013) #P51. [doi:10.37236/2717](https://doi.org/10.37236/2717). Proposition 2.1 is the 12-bowler nonexistence.
3. E. R. Lamken, "Existence results for generalized balanced tournament designs with block size 3", *Des. Codes Cryptogr.* 3 (1992) 33–61.
4. J. Yin, J. Yan, C. Wang, "Generalized balanced tournament designs and related codes", *Des. Codes Cryptogr.* 46 (2008) 211–230.
5. D. Miller, I. Valkov, R. J. R. Abel, "Combinatorial solutions to the Social Golfer Problem and Social Golfer Problem with Adjacent Group Sizes", [arXiv:2507.23376](https://arxiv.org/abs/2507.23376) (2025).
6. G. Ge, C. W. H. Lam, A. C. H. Ling, H. Shen, "Resolvable maximum packings with quadruples", *Des. Codes Cryptogr.* 35 (2005) 287–302. [doi:10.1007/s10623-003-6739-6](https://doi.org/10.1007/s10623-003-6739-6).
7. M. Schüler, A. Schürmann, "Sailing league problems", *J. Combin. Des.* 32 (2024) 171–189. [arXiv:2212.02865](https://arxiv.org/abs/2212.02865).
8. K. Bhandari, "A software solution to the unsolved problem of scheduling bowling tournaments", McKendree University Scholars, issue 13.

References 3, 4 and 6 were seen only as cited by the others; 1, 2 and 5 were read in full.

## 13. Extension to 40 bowlers

This section was added on 24 November 2026. The library now covers 3-way 30, 33, 36 and 39 and 4-way 32, 36 and 40, each with one-round, vacancy and two-round files, plus oil-pattern files for the λ = 2 and λ = 3 sizes. **Every new file is lane-exact.** Code and full notes: `3way/tools/ext40/` and `4way/tools/ext40/` (with `fable32/` and `fable40/`).

**3-way**
- **33 and 39 (Kirkman):** Z_11 × 3 and Z_13 × 3 with the lane pairs rotated, one base week plus 5 or 6 invariant weeks. The vacancy files are the main design with slot N empty, already exact for everyone, so the short group moves around. The two-round files are pairs of KTS found together (as for 27).
- **36:** Z_12 × 3, two base weeks plus 11 invariant weeks. Vacancy: 1-rotational Z_35 ∪ {∞}. Two rounds: a pair of Z_12 designs found together, no repeated trios.
- **30:** Z_10 × 3 **cannot** work: reducing differences mod 2, every trio and invariant week has an even number of odd-difference pairs, but each class needs 5. Instead Z_5 acts on 6 classes, with the 10 lane pairs as two tracks of 5. Two rounds: `second_round`, 5 repeated trios.
- **Oil:** 30 is [14, 9, 6] and 36 is [16, 10, 9], both the lower bound of 3. For 36 the 24-bowler template (a full orbit plus invariant weeks as the first block) fails by the same parity argument; the working split is one orbit plus 4 invariant weeks, then the other orbit's two halves with 4 and 3.

**4-way**
- **36:** plain Z_9 × 4 stalled; tying the three base weeks with a class map φ = (0)(1 2 3) (base week w+1 = φ(base week w)) gives designs in seconds, the tenth lane-exact. The same trick solves 4-way 20 instantly.
- **32:** a fixed-point-free involution symmetry g must fix a lane pair (the couple {x, gx} meets 3 times, an odd number, so some g-invariant group lies in a g-invariant week). That rules out Z_8 on 8 lane pairs and Z_4 on two tracks of 4, which is why the first attempts stalled at 16 cells off. The working design: Z_7 × 4 classes plus 4 fixed bowlers, with i → i+1 rotating lane pairs 1–7 and fixing lane pair 8; 4 base weeks × 7 plus 3 invariant weeks; an extra order-3 map α: (c, i) → (π(c), 2i) makes it searchable. Lanes reduce to residues and solve at once.
- **32 oil: [8, 7, 8, 8], the lower bound of 4.** The same design: a base week's 7 translates are clash-free iff it uses no pair-orbit twice, and with weeks W, αW, α²W, an α-invariant W0 and T, αT, α²T, the blocks are [αᵏW orbit + αᵏT] for k = 0, 1, 2 and [W0 orbit].
- **36 oil: 11 blocks, not improved.** Three Z_9 orbits plus 8 invariant weeks as the fourth block is **impossible**: 8 clash-free transversal weeks would give a (9,4;1) difference matrix over Z_9, i.e. two orthogonal orthomorphisms of Z_9, and an exhaustive check of all 225 normalised orthomorphisms finds none. Order-3-tied variants, five-block splits and untied annealing (floor 18) also failed.
- **40 (λ = 1): the lines of PG(3,3).** Points GF(81)*/GF(3)* = Z_40; the order-5 Singer subgroup n → n+8 acts freely on points and lines. Parallelisms (13 disjoint spreads = weeks) invariant under it with 3 fixed spreads and 2 orbits of 5: 176 of them, enumerated in seconds. The 10 lane pairs are two tracks of 5 rotated with the weeks; an exact solver (choose each base block's track, then two independent memoised DFSs) is exhaustive in 1–3 s per parallelism. 48 of 176 admit exact lanes. This shows a **lane-exact resolvable (40,4,1)** exists. Z_10 × 4 found no design, and Z_13-developed designs can't rotate 10 lane pairs.

**Two rounds in oil blocks, 3-way 18 (`v18_oil_x2`): [8, 5, 6, 7, 8], optimal.** Round 1 is `v18_oil` unchanged. Round 2 is X (2 weeks) + Y (7) + Z (8): Z is an NKTS(18) missing a 1-factor F′ (round 1's first block relabelled), and X + Y is a 9-week resolvable covering whose doubled couples are exactly F′, once in each. X shares no couple with round 1's last 4 weeks, so those join it as block 3. The covering came from z3 with an order-3 automorphism, and was fitted onto round 1 by a graph-isomorphism test (two couple-disjoint weeks form a cubic bipartite graph on 6 + 6 trios); only 34 week pairs are admissible because week 18 must give each bowler the one position they are owed. Lanes by z3. Prefix spread 2 only at weeks 9, 10 and 25; 3 trios recur from round 1 (at least 2 are forced). This result was first reported by another AI system without a schedule; it was rebuilt and verified here.

**4-way 24 oil: [6, 5, 6, 6], exact lanes, prefix spread 2 (third pass).** This settles the 4-block question for 24, including the lane-exact version; another AI system had reported a 6+6+6+5 design without publishing it.
- Points are 6 super-points × Z₂². Z₂² fixes every block: each week is fixed by all of Z₂², or is one of a pair {W, τW} with W fixed by one involution. A week's couples are then whole Z₂²-classes (60 cross classes of 4 couples, 18 inner classes of 2), and the design is an exact cover: every class in exactly 3 of the 4 blocks, chosen from 11,580 invariant weeks and 368,640 week pairs.
- An order-3 map σ = (0 1 2)(3 4 5) on the super-points cycles the three 6-week blocks and fixes each week of the 5-week block. A DFS with forced classes finds the first block for a given 5-week block in seconds.
- σ also rotates the lane pairs in two tracks of three; annealing over the remaining lane choices found an exact assignment for one of 97 designs.
- The four leaves are disjoint, so the worst prefix spread is 2 for any week order.
- **Ruled out on the way:** all 23 weeks Z₂²-invariant with σ (exhaustive); any lane assignment equivariant under Z₂² (counting); a Z₄ analogue (counting). Unsymmetric annealing, and annealing under Z₃ or Z₆ alone, stalled. Code: `4way/tools/oil_search/v24_4block_v3/`.

## 14. Results from Astra, checked independently (24 November 2026)

Astra (another AI agent) worked on the open problems against revision `e5afce7`. Its write-up, certificates and the independent checkers are in [contrib/astra-2026-11-24](contrib/astra-2026-11-24/README.md). Every stated property was reproduced from the weeks alone.

- **12 in fours, fewest repeats.** There are exactly five resolvable 2-(12,4,3) designs (Morales and Velarde 2001), and none can repeat a foursome. Each has a unique resolution. Exhaustive splitting gives minima of 40 for 3 blocks and 27 for 4. So `4w12-oil` is optimal.
- **Lane-exact one-meeting fours.**
  - A quadrupling construction takes *m* to 4*m*, using OA(6,*m*) plus a 4-colouring of each lane's groups.
  - It gives 28·4^j and 40·4^j bowlers. The 112, 160, 448 and 640 witnesses were checked.
- **Vacancy.** Marking any bowler of a lane-exact full round as empty spreads the short group evenly. The reverse also holds, so this is possible exactly when a lane-exact full round exists.
- **Two-round oil.**
  - 4-way 20 reaches 8 blocks, which is optimal. 3-way 24 reaches 6, against a lower bound of 5.
  - The bound is *g* − 1 + ⌈(*t*+*r*)/*L*⌉, from greedy cutting of the fixed round 1.
  - Main-round continuations are optimal for 3-way 18 (6) and 4-way 20 (19).
- **24 in fours, spread 1.** This needs a 7-week clash-free packing whose unmet couples form six disjoint 4-cycles. None has been found yet.

The vacancy result is now used for the library's vacancy files (section 5). The other witnesses are not library files. See OPEN_PROBLEMS.md for what is still open.

### Second batch (24 November 2026)

Checked in [contrib/astra-2026-11-24b](contrib/astra-2026-11-24b/README.md), against revision `33d41db`.

- **Lane-exact one-meeting fours** at 52, 64, 76, 100, 124, 136 and 148 (layered cyclic and finite-field constructions). Below 160 only 88 remains open.
- **36 in fours, four oil patterns** (9+9+9+8) from GF(9) layers on the Hamilton cycles of K_4, lane-exact with spread 2.
- **Two-round oil with round 1 fixed:** 12 witnesses. Seven are proven optimal, including two by exhaustive boundary checks (4-way 24 main and 4-way 32).
- **Qualifying:** 33 draws scored with our own `model.evaluate`. 24 improve the published draw, and new lower bounds come from permutation arrays, the non-existence of two orthogonal Latin squares of order 6, and the seven KTS(15).

Library files taken from this batch: `4way/v36_oil`, the two-round files listed in section 6, and 24 qualifying draws (`qualifying/schemes.json`). `tools/import_astra_b2.py` imports them and asserts that each round 1 matches the library.

### Third batch (24 November 2026)

Checked in [contrib/astra-2026-11-24c](contrib/astra-2026-11-24c/README.md), against revision `61eecc0`.

- **3-way 36, two rounds, oil first: 5 patterns (16+10+12+16+16), optimal.** Round 2 is three 12-bowler layers (11 internal weeks each) plus two 12-week transversal systems built from GF(4) on matched four-bowler groups. Lanes come from annealing inside three sets of four lane pairs. Now `3way/v36_oil_x2`.
- **Qualifying 3×4 at 11 blocks:** a draw optimal on all ten score fields, found with an order-3 symmetry.
- **Hybrids 27 (0/1/8) and 39 (0/1/12):** a one-meeting fours round on 28 or 40 with one bowler removed. Both are the shortest possible.
- **Proofs:**
  - No reordering of the main 4-way 20, 24 or 36 files reaches spread 2 (rechecked here with a direct z3 model over week orders).
  - The 8-week class of the 4-pattern 36 round can't follow the main round's last block under any relabelling (rechecked structurally).
  - A one-meeting 5×3 draw at 6 blocks would have to have no symmetry (19 prime-order cases searched).

### Fourth batch (25 November 2026)

Checked in [contrib/astra-2026-11-25](contrib/astra-2026-11-25/README.md), against revision `054c531`.

- **3-way 24, two rounds: 5 patterns with the oil round first (11+6+8+10+11), 18 with the main round first.** Both meet the lower bound. Round 2 is built as clash-free parts of 2, 10 and 11 weeks. The 11 weeks are a nearly Kirkman triple system, made by doubling an order-3 invariant 12-point design. The 10 weeks have an order-3 symmetry, and the 2 opening weeks are rebuilt from the 10 weeks' unmet couples. Lanes come from a symmetric search, with positions by bipartite flows. Now `3way/v24_oil_x2` and `3way/v24_x2`.
- **Qualifying 5×3 at 6 blocks needs 2 meetings.** Astra split the search into 41 cases by how often bowlers repeat a lane within 4 blocks. It was rechecked here by a single exact-cover search over lane words, with one word fixed as 001234 by relabelling blocks and lanes. That search takes 1.4 s and visits 11.2 million nodes. It finds draws at once when 2 meetings are allowed.
- **4-way 24, trades from the published 7-week packing:** keeping any 3 weeks and refilling the other 4 gives 7 other packings, all relabellings of the original. So trades of up to 4 weeks at a time never remove the 8 unmet triangles.

## 15. Hybrid single rounds

A hybrid round changes the format during the season so that **every couple meets exactly once**. Weeks can be 2-way, 3-way or 4-way, or a mix within a week. Every bowler gets the same number of weeks of each format. The model is North City Singles 2019: 24 bowlers, 10 weeks of 3-way plus 1 week of 4-way.

- **One format a week** (a uniformly resolvable design):
  - The literature settles most two-format cases: Rees 1987 for {2,3}, Dinitz–Ling–Danziger 2009 for {2,4}, and Schuster 2013 for {3,4}.
  - Designs were built with cyclic base-class searches and z3, and the library's own RBIBDs were split.
  - Further designs: resolvable transversal designs over GF(8) and GF(9) with the groups filled in (32 and 36), z3 on designs with half or a third as many points then each point split into 2 or 3 bowlers, and splitting a 4-way week into three 2-way weeks or re-resolving weeks by exact cover.
- **Mixed weeks:** no published results were found.
  - Designs were built by annealing, mostly over Z_m × classes plus fixed points, with base weeks developed mod m and invariant weeks.
  - These are the only option for odd sizes not divisible by 3.
  - Two cases were proved impossible by z3 after hand-normalising: 19 in 7 weeks (3×3-way + 4×4-way) and 14 in 5 weeks (1×2-way + 4×4-way). Symmetric searches (Z_6, Z_3, S_3) for 37 with no 2-way weeks gave no answer within an hour per case.
- **Lanes and positions:** solved afterwards with z3 or annealing. Where a week has fewer groups than lane pairs, the empty lane pairs rotate. Where it helped, two 2-way matches share a lane pair ("wrapped").
- **The 2019 schedule:** reassigning the lanes for the same weeks makes it lane-exact. The original had 22 bowlers off.

Results, proofs of the shortest possible seasons, and open cases are in [hybrid/README.md](https://github.com/Ball-Christopher/matchplay-schedules/blob/main/hybrid/README.md). The checker is `hybrid/verify.py`.
