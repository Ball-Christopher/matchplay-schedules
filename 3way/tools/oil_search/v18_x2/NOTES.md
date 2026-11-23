# 3-way 18, two rounds in oil-pattern blocks: [8, 5, 6, 7, 8]

Output: `3way/v18_oil_x2.json` / `.toml` (34 weeks; weeks 1-17 = `v18_oil` unchanged).

## Structure
Round 2 = X (2 weeks) + Y (7) + Z (8). Block 3 = v18_oil's weeks 14-17 (C) + X.
Any clash-free 8-week block is an NKTS(18) missing a 1-factor F', so X+Y must be a 9-class
resolvable covering with excess F', each F' couple once in X and once in Y.

## What constrains X
- X's trios must be triangles in the complement of C's couples: only 93 such triangles,
  1707 parallel classes, 15,641 couple-disjoint pairs of classes (`diag.py`).
- Positions: after round 1 every bowler is one short in exactly one position (6/6/6), so to
  stay within one after week 18 each week-18 trio must hold one bowler owed each position.
  Only 2 of the 1707 classes are transversal like that -> 34 admissible X (`out/xcands.json`).
  Every one of them reuses >= 2 round-1 trios (from blocks 1-2), so 0 repeats is impossible
  with strict positions.
- v18_oil's own covering (weeks 9-17) has no 2+7 re-split (no 2 weeks hold all 9 F couples).

## Pipeline (about 2 s once known)
1. `sym_cover.py`: z3 (QF_FD), fixed-point-free order-3 automorphism, week orbits
   X: 1+1 invariant; Y: 3-orbit + 1 + 1 ("early") and 1 + 1 ("late"); X + early Y clash-free,
   so F' recurs only in Y's last two weeks. sat in ~1 s per seed.
2. `match.py`: two couple-disjoint weeks = cubic bipartite graph on 6+6 trios, bowlers = its
   18 edges. Relabelling X onto an admissible pair = graph isomorphism; all isomorphisms
   enumerated, fewest round-1 trios in X+Y kept. Of the first 195 seeds scanned (of 249 run): 109 matched one of the 34
   (others have a different graph type); best repeats 3 (10 seeds; 2, the floor, never seen), then 4/5/6. Seed 2 used.
3. `finish.py`: Z = v18_oil's block 1 relabelled so F -> F' (hill-climb over 9!*2^9: 0 repeated
   trios); Y order by exhaustive search on prefix spread; lanes by z3 against round 1's counts
   (sat in 0.2 s); week 18 positions = owed positions, weeks 19-34 `positions.assign`.
4. `build.py`: re-checks everything from the weeks and writes the library files.

## Result
- Blocks 8, 5, 6, 7, 8 all clash-free; round 2 is itself a resolvable 2-(18,3,2).
- Lanes exact (5 or 6 everywhere); positions 11/12 and within one after every week.
- Prefix spread 2 at weeks 9, 10 (round 1) and 25 only. One week at 2 in round 2 is the
  minimum for this block order: F' needs >= 2 weeks of Y for its second meetings.
- 3 round-2 trios also occur in round 1: (2,7,16), (3,5,12), (9,15,17); none at the join;
  none repeated inside round 2.

## What failed / was dropped
- `cover_z3.py` (first version, joint, no round-1 trio allowed anywhere): unsat in 0.1 s
  (the transversal week cannot avoid round-1 trios).
- `cover_z3.py` (X fixed to a candidate, z3 for Y without symmetry) and `cover_joint.py`
  (X free): no answer in ~10 min on 16 jobs; killed once the symmetric route worked.
- Not tried: 3+7+7 / 3+6+8 / 4+5+8 round-2 splits (458 triples of disjoint classes exist).
