# 4-way 40: lane-exact v40 and v40_vacant (24 Nov 2026)

**Result: a lane-exact resolvable 2-(40,4,1) exists.** `4way/v40` and `4way/v40_vacant` are now exact
(every bowler on every lane pair 1 or 2 times; couples once; positions 4/3/3/3). `python3 verify.py`: ALL OK.
Old files are kept here as `old_v40*.json/.toml`.

## Construction
- **Design:** the lines of PG(3,3). Points = GF(81)\*/GF(3)\* = Z_40 (GF(81) = GF(3)[x]/(x^4+x+2), point n = x^n),
  130 lines of 4 points. A resolution into 13 weeks is a parallelism (13 disjoint spreads).
- **Symmetry:** the order-5 Singer subgroup n → n+8. It is free on points (8 classes n mod 8, each a copy of Z_5)
  and on lines (26 orbits of 5). Take parallelisms it fixes with **3 fixed spreads** (each = 2 line orbits) and
  **2 spread orbits of length 5** (a spread whose 10 lines lie in 10 different line orbits, and its translates).
  `pg33.py` enumerates them all: 9 invariant spreads, 417 spread orbits, **176 parallelisms** (labelled; orbit
  representatives up to translation) in about 2 s.
- **Lanes:** 10 lane pairs = 2 tracks of 5; Z_5 rotates each track and acts on the weeks. A base block on lane
  (t, j) is developed as block+g on lane (t, j+g) (in the same week for fixed weeks, in week+g for orbit weeks).
  Then a point (a, c) of a base block on (t, j) puts bowler (0, c) on lane (t, j−a), so lane balance is
  **8 classes × 10 lanes** (80 cells in {1,2}) instead of 400, with 26 base blocks to place.
- **Exact solver `lz5b.c`:** (1) choose the track of every base block (5 of 10 per orbit week, one of two per fixed
  week); each class must visit each track 5..8 times; (2) given that, the two tracks are independent, each a DFS over
  offsets (3 fixed-week blocks free, two permutations of 5); track problems are memoised by (subset, subset, fixed
  choice) and track 1 is the complementary key. Exhaustive in 1-3 s per design (about 20,000 track splits, 2×10^7 nodes).
- **Outcome:** 48 of the 176 parallelisms have an exact equivariant assignment; for the other 128 the search is a
  proof that no Z_5-equivariant two-track assignment exists. v40 uses parallelism #24 (`finish40.py 24`).
  `pg33_lanes.txt` has one solution for each of the 48.
- **v40_vacant:** the same schedule with player 40 vacant (all 40 are exact, so the 39 stay exact).

## What did not work / not needed
- `lz5.c` (first version, one DFS over all 26 blocks on 10 lanes): 2×10^8 nodes without finishing one design. The
  track decomposition is what makes it instant.
- Ideas not tried because the above succeeded on the first family: Z_9 × 4 ∪ 4 fixed points (a Z_9-equivariant
  lane map would put each fixed point 4 times on the fixed lane pair, so only the Z_3 quotient could act — weak);
  generic SAT on the Z_13 designs; joint SAT.
- Z_13-developed designs cannot have Z_13-equivariant exact lanes: 13 is prime > 10, so every lane pair would carry
  a whole block orbit and ∞ would sit on one lane pair all 13 weeks.

## Follow-up for the library owner
- `4way/v40_x2` was built as "round 1 = v40" from the old v40; it still verifies but its round 1 is no longer the
  current v40. Regenerate with `finish.finish_x2(40)` (ext40/finish.py) if the link should hold.
- README / METHODS / OPEN_PROBLEMS still list v40 and v40_vacant as not exact.

## Compute
About 10 minutes wall in total (enumeration 2 s; lane solve 176 designs in 4 min single core).
