# Hybrid single-round schedules

These schedules let the matchplay format change during the season (2-way, 3-way or 4-way) so that **every couple meets exactly once**. The model is the North City Singles 2019 league. It ran 24 bowlers as 10 weeks of 3-way plus 1 week of 4-way: 11 weeks, one meeting per couple. Pure 3-way can't do this for 24 bowlers, and pure 4-way can't either.

Status: checked by `verify.py` and listed on the website under **Hybrid** (bowling.collapse.nz/schedules). Last search: 24 Nov 2026.

## What "balanced" means here

- **One round:** every couple meets exactly once.
- **Format-fair:** every bowler has the same number of 2-way, 3-way and 4-way weeks. File names give this mix as `a2-a3-a4`; for example, `v24_0-10-1` is 0 two-way, 10 three-way and 1 four-way week. This needs a2 + 2·a3 + 3·a4 = v − 1.
- **Lane-exact:** each bowler is on each lane pair ⌊R/n⌋ or ⌈R/n⌉ times. Here R is the number of weeks and n the number of lane pairs. Weeks with fewer groups leave some lane pairs empty, and the empty ones rotate.
- **Positions:** within each format, each bowler's playing positions are even (differ by at most 1). All files except the 2019 original meet this.
- **"Wrapped" 2-way:** two 2-way matches share one lane pair. This is used only where it was needed to fit or balance the lanes.
- **Uniform vs mixed:** a *uniform* week has one format for everybody. A *mixed* week has groups of different sizes at once, e.g. 11 = 4+4+3. Mixed weeks are the only option for odd sizes not divisible by 3.

## Results (v = bowlers, R = weeks)

86 schedules, 71 of them lane-exact. "Wrapped" counts lane pairs shared by two 2-way matches over the season; in 2-way weeks with more matches than lane pairs every match is wrapped.

| v | mix (2/3/4-way weeks) | R | lane pairs | lanes | wrapped | weeks | note | file |
|---:|---|---:|---:|---|---:|---|---|---|
| 11 | 4 / 3 / 0 | 7 | 5 | exact |  | mixed |  | `v11_4-3-0_mixed` |
| 12 | 0 / 4 / 1 | 5 | 4 | exact |  | uniform | shortest possible | `v12_0-4-1` |
| 12 | 2 / 3 / 1 | 6 | 4 | exact | 4 | uniform |  | `v12_2-3-1` |
| 12 | 3 / 4 / 0 | 7 | 4 | exact | 7 | uniform |  | `v12_3-4-0` |
| 12 | 4 / 2 / 1 | 7 | 4 | exact | 8 | uniform |  | `v12_4-2-1` |
| 12 | 5 / 3 / 0 | 8 | 4 | **1 off** | 10 | uniform | exact impossible for this design | `v12_5-3-0` |
| 12 | 6 / 1 / 1 | 8 | 4 | **1 off** | 12 | uniform | exact impossible for this design | `v12_6-1-1` |
| 12 | 7 / 2 / 0 | 9 | 4 | exact | 15 | uniform |  | `v12_7-2-0` |
| 12 | 8 / 0 / 1 | 9 | 3 | exact | 24 | uniform |  | `v12_8-0-1` |
| 12 | 9 / 1 / 0 | 10 | 4 | exact | 18 | uniform |  | `v12_9-1-0` |
| 13 | 6 / 3 / 0 | 9 | 6 | exact |  | mixed |  | `v13_6-3-0_mixed` |
| 14 | 7 / 0 / 2 | 9 | 7 | exact |  | mixed |  | `v14_7-0-2_mixed` |
| 15 | 0 / 1 / 4 | 5 | 4 | **3 off** |  | mixed | shortest for 15 | `v15_0-1-4_mixed` |
| 15 | 4 / 5 / 0 | 9 | 7 | exact |  | mixed |  | `v15_4-5-0_mixed` |
| 16 | 0 / 3 / 3 | 6 | 5 | exact |  | mixed |  | `v16_0-3-3_mixed` |
| 16 | 3 / 0 / 4 | 7 | 4 | **3 off** | 12 | uniform | 3 off is proven best | `v16_3-0-4` |
| 16 | 6 / 0 / 3 | 9 | 4 | exact | 24 | uniform |  | `v16_6-0-3` |
| 16 | 9 / 0 / 2 | 11 | 4 | exact | 36 | uniform |  | `v16_9-0-2` |
| 16 | 12 / 0 / 1 | 13 | 4 | exact | 48 | uniform |  | `v16_12-0-1` |
| 17 | 4 / 6 / 0 | 10 | 7 | exact |  | mixed |  | `v17_4-6-0_mixed` |
| 18 | 1 / 8 / 0 | 9 | 6 | exact | 3 | uniform | NKTS | `v18_1-8-0` |
| 18 | 3 / 7 / 0 | 10 | 6 | exact | 10 | uniform |  | `v18_3-7-0` |
| 18 | 5 / 6 / 0 | 11 | 6 | exact | 15 | uniform |  | `v18_5-6-0` |
| 18 | 7 / 5 / 0 | 12 | 6 | **1 off** | 22 | uniform | exact impossible for this design | `v18_7-5-0` |
| 18 | 9 / 4 / 0 | 13 | 6 | exact | 30 | uniform |  | `v18_9-4-0` |
| 18 | 11 / 3 / 0 | 14 | 6 | exact | 35 | uniform |  | `v18_11-3-0` |
| 19 | 6 / 6 / 0 | 12 | 8 | exact |  | mixed |  | `v19_6-6-0_mixed` |
| 20 | 4 / 0 / 5 | 9 | 5 | exact | 20 | uniform | shortest possible | `v20_4-0-5` |
| 20 | 7 / 0 / 4 | 11 | 5 | exact | 35 | uniform |  | `v20_7-0-4` |
| 20 | 10 / 0 / 3 | 13 | 5 | exact | 50 | uniform |  | `v20_10-0-3` |
| 21 | 2 / 3 / 4 | 9 | 7 | **4 off** |  | mixed |  | `v21_2-3-4_mixed` |
| 21 | 6 / 7 / 0 | 13 | 9 | exact |  | mixed |  | `v21_6-7-0_mixed` |
| 22 | 3 / 0 / 6 | 9 | 6 | exact | 12 | mixed | shortest for 22 | `v22_3-0-6_mixed` |
| 22 | 9 / 3 / 2 | 14 | 10 | exact |  | mixed |  | `v22_9-3-2_mixed` |
| 23 | 4 / 3 / 4 | 11 | 9 | exact | 7 | mixed |  | `v23_4-3-4_mixed` |
| 23 | 4 / 9 / 0 | 13 | 10 | exact |  | mixed |  | `v23_4-9-0_mixed` |
| 24 | 0 / 1 / 7 | 8 | 8 | **12 off** |  | uniform | exact impossible; ≥ 1 off | `v24_0-1-7` |
| 24 | 0 / 4 / 5 | 9 | 8 | exact |  | uniform |  | `v24_0-4-5` |
| 24 | 0 / 7 / 3 | 10 | 8 | **1 off** |  | uniform |  | `v24_0-7-3` |
| 24 | 1 / 5 / 4 | 10 | 8 | exact | 4 | uniform |  | `v24_1-5-4` |
| 24 | 2 / 3 / 5 | 10 | 8 | exact | 10 | uniform |  | `v24_2-3-5` |
| 24 | 3 / 1 / 6 | 10 | 8 | exact | 14 | uniform |  | `v24_3-1-6` |
| 24 | 0 / 10 / 1 | 11 | 8 | exact |  | uniform | 2019 weeks, re-laned (original 22 off) | `v24_0-10-1` |
| 24 | 1 / 8 / 2 | 11 | 8 | exact | 5 | uniform |  | `v24_1-8-2` |
| 24 | 2 / 6 / 3 | 11 | 8 | exact | 9 | uniform |  | `v24_2-6-3` |
| 24 | 3 / 4 / 4 | 11 | 8 | exact | 13 | uniform |  | `v24_3-4-4` |
| 24 | 4 / 2 / 5 | 11 | 8 | exact | 17 | uniform |  | `v24_4-2-5` |
| 24 | 5 / 0 / 6 | 11 | 6 | exact | 30 | uniform | Schuster–Ge A.15 | `v24_5-0-6` |
| 24 | 1 / 11 / 0 | 12 | 8 | exact | 4 | uniform | NKTS | `v24_1-11-0` |
| 24 | 2 / 9 / 1 | 12 | 8 | exact | 9 | uniform |  | `v24_2-9-1` |
| 24 | 3 / 7 / 2 | 12 | 8 | exact | 14 | uniform |  | `v24_3-7-2` |
| 24 | 4 / 5 / 3 | 12 | 8 | exact | 18 | uniform |  | `v24_4-5-3` |
| 24 | 5 / 3 / 4 | 12 | 8 | exact | 23 | uniform |  | `v24_5-3-4` |
| 24 | 6 / 1 / 5 | 12 | 8 | exact | 25 | uniform |  | `v24_6-1-5` |
| 24 | 3 / 10 / 0 | 13 | 8 | exact | 12 | uniform |  | `v24_3-10-0` |
| 24 | 4 / 8 / 1 | 13 | 8 | exact | 19 | uniform |  | `v24_4-8-1` |
| 24 | 5 / 6 / 2 | 13 | 8 | exact | 21 | uniform |  | `v24_5-6-2` |
| 24 | 6 / 4 / 3 | 13 | 8 | exact | 27 | uniform |  | `v24_6-4-3` |
| 24 | 7 / 2 / 4 | 13 | 8 | exact | 29 | uniform |  | `v24_7-2-4` |
| 24 | 8 / 0 / 5 | 13 | 6 | exact | 48 | uniform |  | `v24_8-0-5` |
| 24 | 5 / 9 / 0 | 14 | 8 | exact | 20 | uniform |  | `v24_5-9-0` |
| 24 | 6 / 7 / 1 | 14 | 8 | exact | 27 | uniform |  | `v24_6-7-1` |
| 24 | 7 / 5 / 2 | 14 | 8 | exact | 29 | uniform |  | `v24_7-5-2` |
| 24 | 8 / 3 / 3 | 14 | 8 | exact | 33 | uniform |  | `v24_8-3-3` |
| 24 | 9 / 1 / 4 | 14 | 8 | exact | 40 | uniform |  | `v24_9-1-4` |
| 25 | 6 / 3 / 4 | 13 | 8 | exact | 24 | mixed |  | `v25_6-3-4_mixed` |
| 26 | 7 / 3 / 4 | 14 | 11 | exact |  | mixed |  | `v26_7-3-4_mixed` |
| 27 | 6 / 4 / 4 | 14 | 11 | exact |  | mixed |  | `v27_6-4-4_mixed` |
| 28 | 3 / 0 / 8 | 11 | 7 | exact | 21 | uniform |  | `v28_3-0-8` |
| 28 | 6 / 0 / 7 | 13 | 7 | **1 off** | 42 | uniform |  | `v28_6-0-7` |
| 29 | 4 / 6 / 4 | 14 | 10 | exact | 9 | mixed |  | `v29_4-6-4_mixed` |
| 30 | 1 / 14 / 0 | 15 | 10 | exact | 6 | uniform | NKTS | `v30_1-14-0` |
| 31 | 6 / 6 / 4 | 16 | 10 | exact | 27 | mixed |  | `v31_6-6-4_mixed` |
| 32 | 1 / 0 / 10 | 11 | 8 | exact | 8 | uniform | shortest for 32 | `v32_1-0-10` |
| 32 | 4 / 0 / 9 | 13 | 8 | exact | 32 | uniform | RTD(4,8) | `v32_4-0-9` |
| 35 | 4 / 3 / 8 | 15 | 11 | exact | 24 | mixed |  | `v35_4-3-8_mixed` |
| 36 | 0 / 1 / 11 | 12 | 12 | **19 off** |  | uniform | exact impossible; ≥ 1 off | `v36_0-1-11` |
| 36 | 0 / 4 / 9 | 13 | 12 | exact |  | uniform | RTD(4,9) + KTS(9) | `v36_0-4-9` |
| 36 | 1 / 2 / 10 | 13 | 12 | **11 off** | 7 | uniform |  | `v36_1-2-10` |
| 36 | 2 / 0 / 11 | 13 | 9 | exact | 18 | uniform |  | `v36_2-0-11` |
| 36 | 0 / 7 / 7 | 14 | 12 | **7 off** |  | uniform |  | `v36_0-7-7` |
| 36 | 1 / 5 / 8 | 14 | 12 | **5 off** | 7 | uniform |  | `v36_1-5-8` |
| 36 | 2 / 3 / 9 | 14 | 12 | **3 off** | 12 | uniform |  | `v36_2-3-9` |
| 36 | 3 / 1 / 10 | 14 | 12 | **1 off** | 20 | uniform |  | `v36_3-1-10` |
| 36 | 1 / 17 / 0 | 18 | 12 | exact | 6 | uniform | NKTS | `v36_1-17-0` |
| 40 | 3 / 0 / 12 | 15 | 10 | exact | 30 | uniform |  | `v40_3-0-12` |

`v24_archive2019.json` is the original 2019 schedule with its original lanes, kept for comparison.

## Proven limits

- **12:** at most one 4-way week. Two 4-way weeks on 12 bowlers always repeat a couple, because a foursome in week 2 takes two bowlers from one of week 1's three groups. So 5 weeks is the shortest possible. Also, 12 can't be 3-way with a single 2-way week (NKTS(12) doesn't exist). Every other mix for 12 is in the table.
- **14 in 5 weeks (1×2-way + 4×4-way): impossible** (z3, `tools/mixed/sat_p0.py`).
- **16, 7 weeks (4 four-way + 3 two-way):** the four 4-way weeks are forced to be AG(2,4). z3 shows 3 bowlers off is the best possible.
- **19 in 7 weeks (3×3-way + 4×4-way): impossible.** Computer-assisted: z3 shows every bowler is in at most one foursome of the 4-way weeks, which forces a 3×4 grid, and the remaining cases are unsat. The chain is in the `tools/mixed/sat19.py` docstring.
- **20:** six 4-way weeks with no repeat is impossible (social golfer 5-4-6), so 9 weeks is the shortest possible. 1×2-way + 6×4-way is a known exception in the literature.
- **24, 8 weeks (7 four-way + 1 three-way):** each lane pair gets 3 + 4x visits, never the 24 that exact lanes need. So at least 1 bowler is off (one bowler on the two busiest lane pairs 4 times each could absorb it). Best found: 12.
- **36, 12 weeks (11 four-way + 1 three-way):** the same argument (3 + 4x is never 36), so at least 1 off. Best found: 19.
- **30 and 40:** no uniform hybrid fits in 14 weeks.
- The literature (`LITERATURE.md`) covers uniform hybrids with two formats; see Rees 1987, Dinitz–Ling–Danziger 2009 and Schuster 2009/2013. Explicit 24-bowler designs are printed in Schuster 2009 and Schuster–Ge 2010. Nothing published covers mixed weeks, the same mix for every bowler, or lane balance in any hybrid.

## Open (not found, not proven impossible)

- **Uniform:** 24 with 2×2-way + 7×4-way (also open in the literature), and 24 with 1×2-way + 2×3-way + 6×4-way. Better lanes for 24 in 8 weeks (1–12 off) and the 36 files that are not exact.
- **37: no schedule yet within 16 weeks.** Not found: 0/6/8 in 14 weeks, 0/12/4 in 16, or 6/3/8 in 17. Many symmetry groups are ruled out (Z_9, Z_12, Z_18, Z_36, A_4, and Z_2×Z_2 for 0/6/8); Z_6 templates gave no answer in an hour each.
- **Mixed, only 3-way and 4-way groups:** 25 in 10 weeks (0/6/4), and 31 in 11 or 13 (0/3/8, 0/9/4).
- **Other mixed options not found:** 21 0/4/4, 26 1/0/8 and 7/0/6, 27 0/1/8, 33 4/2/8, 34 3/3/8 and 3/0/10, 38 1/3/10; 39 not attempted.

## Practical caveats

- In a mixed week some bowlers play 1 opponent, others 2 or 3. Format fairness evens this out over the season, but week-by-week points aren't comparable across groups of different sizes.
- Several mixed files have a lot of 2-way matches in one week, so they need wrapped lane pairs to stay lane-exact. For 25, 29, 31 and 35 the wrap counts are the minimum those weeks allow at their lane-pair counts (`tools/mixed/lanes_anneal.py`). No-wrap versions on more lane pairs are in `tools/mixed/raw/nowrap/` (29 on 11, 31 on 12).
- In a λ = 1 round the couple counts after any week are 0 or 1, so a season stopped early is as even as it can be (prefix spread 1).

## Files

- `verify.py`: the checker (`python3 verify.py`).
- `profiles.py`: which format mixes are possible for each size, by counting.
- `files/`: the schedules.
- `tools/uniform/`, `tools/mixed/`: the search code.
- `LITERATURE.md`: the literature check. Some citations came from search snippets and need confirming before anything is published.
