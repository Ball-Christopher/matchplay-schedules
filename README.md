# Balanced matchplay schedules

Balanced schedules for 3-way and 4-way matchplay bowling leagues of 11–40 bowlers.
Every couple of bowlers meets equally often, and every bowler gets an even share of the lane pairs
and of the bowling positions. Each schedule is a JSON file and a ready-to-paste `[schedule]` TOML block
(`pattern = 3` or `4` in the season file of the league engine).

- **Pick a schedule, add names and export it (CSV, TOML, JSON, print):** [`docs/index.html`](docs/index.html),
  also at <https://bowling.collapse.nz/schedules/>.
- **How they were made, the limits and the open questions:** [`docs/methods.html`](docs/methods.html)
  (source [METHODS.md](METHODS.md)).
- **Open problems, stated on their own:** [OPEN_PROBLEMS.md](OPEN_PROBLEMS.md).
- **Open issues, as a to-do list with where to start:** [OPEN_ISSUES.md](OPEN_ISSUES.md).
- **Outside results, checked here:** [contrib/astra-2026-11-24](contrib/astra-2026-11-24/README.md).
- **Hybrid seasons** (the format changes between 2-, 3- and 4-way so every couple meets exactly once): [hybrid/README.md](hybrid/README.md). They're also on the web page under "Hybrid".
- **Qualifying lane movements** (M pairs, K per pair, B blocks: mixing, following and lane-pair balance): [qualifying/README.md](qualifying/README.md).

## Reading a schedule
- Each week is a permutation of roster numbers 1..N, read in groups of 3 or 4.
- Group g bowls on lane pair g, counting from `first_lane` up. With `pattern = 4` this is the engine's `lane_pair()` mapping.
- Within a group the order is the bowling position:
  - 3-way: left lane 1st, right lane 1st, left lane 2nd.
  - 4-way: left lane 1st, right lane 1st, left lane 2nd, right lane 2nd.
- The engine scores each pairing in a group, so a 4-way night is worth up to 3 × 14 points.

## Files per roster size
| File | What it is |
|---|---|
| `v{N}` | One round: every couple shares a group the same number of times. |
| `v{N}_vacant` | For N−1 bowlers. Roster number N is an empty slot, so that group plays a bowler short. Balance is judged on the real bowlers. |
| `v{N}_x2` | Two rounds. Round 1 has the same groups and lane pairs as `v{N}`, so you can stop after it. Round 2 tops up each bowler's lane counts and avoids repeating round 1's groups. |

## Balance achieved
Every file:
- **Couples:** every couple meets exactly λ times.
- **Positions:** every bowler holds each position ⌊r/k⌋ or ⌈r/k⌉ times, and stays within one of even after every week.
- **Lane pairs:** see the tables.

### 3-way
| N | weeks | each couple meets | lanes: single | vacant | two rounds |
|---|---|---|---|---|---|
| 12 | 11 | 2 | exact | exact | exact |
| 15 | 7 | 1 | 1 bowler off (**exact is impossible**: all 7 KTS(15) checked) | exact | exact |
| 18 | 17 | 2 | exact | exact | exact |
| 21 | 10 | 1 | exact | exact | exact |
| 24 | 23 | 2 | exact | exact | exact |
| 27 | 13 | 1 | exact | exact | exact |
| 30 | 29 | 2 | exact | exact | exact |
| 33 | 16 | 1 | exact | exact | exact |
| 36 | 35 | 2 | exact | exact | exact |
| 39 | 19 | 1 | exact | exact | exact |

### 4-way
| N | weeks | each couple meets | lanes: single | vacant | two rounds |
|---|---|---|---|---|---|
| 12 | 11 | 3 | 1 bowler off (**exact is impossible**: no GBTD(4,3), Chee–Kiah–Wang 2013) | exact | exact |
| 16 | 5 | 1 | not exact (**exact is impossible** for AG(2,4)) | 3 off (also impossible) | exact |
| 20 | 19 | 3 | exact | exact | exact |
| 24 | 23 | 3 | exact | exact | exact |
| 28 | 9 | 1 | exact | exact | exact |
| 32 | 31 | 3 | exact | exact | exact |
| 36 | 35 | 3 | exact | exact | exact |
| 40 | 13 | 1 | exact (PG(3,3); first known lane-exact resolvable (40,4,1)) | exact | exact |

### Oil-pattern blocks
For leagues that change oil pattern in blocks, the aim is that no couple meets twice on the same pattern, using as few patterns (blocks of consecutive weeks) as possible. Block lengths are free. The block lengths are stored as `blocks`, or `oil_blocks` in existing files, and given in the TOML header.

| File | Patterns (weeks each) | Same-pattern repeats | Lanes | Notes |
|---|---|---|---|---|
| 3way/v12 | 3 (4,3,4) | 0 | exact | the existing schedule is already ideal (lower bound 3) |
| 3way/v18_oil | 3 (8,5,4) | 0 | exact | lower bound reached |
| 3way/v24_oil | 3 (11,6,6) | 0 | exact | lower bound reached |
| 3way/v30_oil | 3 (14,9,6) | 0 | exact | lower bound reached |
| 3way/v36_oil | 3 (16,10,9) | 0 | exact | lower bound reached |
| 3way/v18_oil_x2 | 5 (8,5,6,7,8) over two rounds | 0 | exact | round 1 = v18_oil; 5 is optimal |
| 3way/v24_oil_x2 | 6 (11,6,6,11,6,6) | 0 | exact | round 1 = v24_oil; lower bound 5 (Astra) |
| 3way/v30_oil_x2 | 5 (14,9,8,13,14) | 0 | exact | round 1 = v30_oil; optimal (Astra) |
| 3way/v36_oil_x2 | 6 (16,10,9,16,10,9) | 0 | exact | round 1 = v36_oil; lower bound 5 (Astra) |
| 4way/v24_oil_x2 | 8 (6,5,6,6,6,5,6,6) | 0 | exact | round 1 = v24_oil; optimal (Astra) |
| 4way/v32_oil_x2 | 8 (8,7,8,8,8,7,8,8) | 0 | exact | round 1 = v32_oil; optimal (Astra) |
| 4way/v36_oil_x2 | 8 (9,9,9,8,9,9,9,8) | 0 | exact | round 1 = v36_oil; lower bound 7 |
| 4way/v12_oil | 4 (2,3,3,3) | 27 | 1 off | repeats unavoidable: any two weeks of 12 in fours share a couple |
| 4way/v20_oil | 4 (5,4,5,5) | 0 | exact | lower bound reached |
| 4way/v32_oil | 4 (8,7,8,8) | 0 | exact | lower bound reached |
| 4way/v36_oil | 4 (9,9,9,8) | 0 | exact | lower bound reached; prefix spread 2 (Astra) |
| 4way/v24_oil | 4 (6,5,6,6) | 0 | exact | lower bound reached; prefix spread 2 |
| two-round files for 3way 15/21/27/33/39 and 4way 16/28/40 | 2 (one per round) | 0 | exact | each couple meets once on each pattern |

`prefix_spread` in each JSON is the max − min of couple meetings after each week. It tells you how even a season that stops early would be.

## Schedules by ID
IDs are `{k}w{N}` plus `-vacant`, `-x2`, `-oil` or `-oil-x2`: `4w20-oil` is 4-way, 20 slots, one round in oil-pattern blocks.
A `-vacant` schedule is for N−1 bowlers. The table is written by `tools/build_pages.py` from the files.

<!-- catalogue:start -->
| ID | Bowlers | Weeks | Couples meet | Lane pairs | Oil patterns / hybrid formats | File |
|---|---|---|---|---|---|---|
| `3w12` | 12 | 11 | 2× | exact | 4+3+4 | [3way/v12.toml](3way/v12.toml) |
| `3w12-vacant` | 11 (slot 12 empty) | 11 | 2× | exact |  | [3way/v12_vacant.toml](3way/v12_vacant.toml) |
| `3w12-x2` | 12 | 22 | 4× | exact | 4+3+4+3+4+4 | [3way/v12_x2.toml](3way/v12_x2.toml) |
| `3w15` | 15 | 7 | 1× | 1 bowler(s) off |  | [3way/v15.toml](3way/v15.toml) |
| `3w15-vacant` | 14 (slot 15 empty) | 7 | 1× | exact |  | [3way/v15_vacant.toml](3way/v15_vacant.toml) |
| `3w15-x2` | 15 | 14 | 2× | exact | 7+7 | [3way/v15_x2.toml](3way/v15_x2.toml) |
| `3w18` | 18 | 17 | 2× | exact |  | [3way/v18.toml](3way/v18.toml) |
| `3w18-vacant` | 17 (slot 18 empty) | 17 | 2× | exact |  | [3way/v18_vacant.toml](3way/v18_vacant.toml) |
| `3w18-x2` | 18 | 34 | 4× | exact |  | [3way/v18_x2.toml](3way/v18_x2.toml) |
| `3w18-oil` | 18 | 17 | 2× | exact | 8+5+4 | [3way/v18_oil.toml](3way/v18_oil.toml) |
| `3w18-oil-x2` | 18 | 34 | 4× | exact | 8+5+6+7+8 | [3way/v18_oil_x2.toml](3way/v18_oil_x2.toml) |
| `3w21` | 21 | 10 | 1× | exact |  | [3way/v21.toml](3way/v21.toml) |
| `3w21-vacant` | 20 (slot 21 empty) | 10 | 1× | exact |  | [3way/v21_vacant.toml](3way/v21_vacant.toml) |
| `3w21-x2` | 21 | 20 | 2× | exact | 10+10 | [3way/v21_x2.toml](3way/v21_x2.toml) |
| `3w24` | 24 | 23 | 2× | exact |  | [3way/v24.toml](3way/v24.toml) |
| `3w24-vacant` | 23 (slot 24 empty) | 23 | 2× | exact |  | [3way/v24_vacant.toml](3way/v24_vacant.toml) |
| `3w24-x2` | 24 | 46 | 4× | exact | 4+1+1+1+1+1+1+1+1+1+1+1+1+1+1+5+11+6+6 | [3way/v24_x2.toml](3way/v24_x2.toml) |
| `3w24-oil` | 24 | 23 | 2× | exact | 11+6+6 | [3way/v24_oil.toml](3way/v24_oil.toml) |
| `3w24-oil-x2` | 24 | 46 | 4× | exact | 11+6+6+11+6+6 | [3way/v24_oil_x2.toml](3way/v24_oil_x2.toml) |
| `3w27` | 27 | 13 | 1× | exact |  | [3way/v27.toml](3way/v27.toml) |
| `3w27-vacant` | 26 (slot 27 empty) | 13 | 1× | exact |  | [3way/v27_vacant.toml](3way/v27_vacant.toml) |
| `3w27-x2` | 27 | 26 | 2× | exact | 13+13 | [3way/v27_x2.toml](3way/v27_x2.toml) |
| `3w30` | 30 | 29 | 2× | exact |  | [3way/v30.toml](3way/v30.toml) |
| `3w30-vacant` | 29 (slot 30 empty) | 29 | 2× | exact |  | [3way/v30_vacant.toml](3way/v30_vacant.toml) |
| `3w30-x2` | 30 | 58 | 4× | exact | 5+4+1+1+2+2+1+1+2+1+1+2+1+1+2+8+9+14 | [3way/v30_x2.toml](3way/v30_x2.toml) |
| `3w30-oil` | 30 | 29 | 2× | exact | 14+9+6 | [3way/v30_oil.toml](3way/v30_oil.toml) |
| `3w30-oil-x2` | 30 | 58 | 4× | exact | 14+9+8+13+14 | [3way/v30_oil_x2.toml](3way/v30_oil_x2.toml) |
| `3w33` | 33 | 16 | 1× | exact |  | [3way/v33.toml](3way/v33.toml) |
| `3w33-vacant` | 32 (slot 33 empty) | 16 | 1× | exact |  | [3way/v33_vacant.toml](3way/v33_vacant.toml) |
| `3w33-x2` | 33 | 32 | 2× | exact | 16+16 | [3way/v33_x2.toml](3way/v33_x2.toml) |
| `3w36` | 36 | 35 | 2× | exact |  | [3way/v36.toml](3way/v36.toml) |
| `3w36-vacant` | 35 (slot 36 empty) | 35 | 2× | exact |  | [3way/v36_vacant.toml](3way/v36_vacant.toml) |
| `3w36-x2` | 36 | 70 | 4× | exact | 2+1+1+1+1+2+2+1+1+3+1+2+1+1+2+1+2+2+2+1+2+11+16+11 | [3way/v36_x2.toml](3way/v36_x2.toml) |
| `3w36-oil` | 36 | 35 | 2× | exact | 16+10+9 | [3way/v36_oil.toml](3way/v36_oil.toml) |
| `3w36-oil-x2` | 36 | 70 | 4× | exact | 16+10+9+16+10+9 | [3way/v36_oil_x2.toml](3way/v36_oil_x2.toml) |
| `3w39` | 39 | 19 | 1× | exact |  | [3way/v39.toml](3way/v39.toml) |
| `3w39-vacant` | 38 (slot 39 empty) | 19 | 1× | exact |  | [3way/v39_vacant.toml](3way/v39_vacant.toml) |
| `3w39-x2` | 39 | 38 | 2× | exact | 19+19 | [3way/v39_x2.toml](3way/v39_x2.toml) |
| `4w12` | 12 | 11 | 3× | 1 bowler(s) off |  | [4way/v12.toml](4way/v12.toml) |
| `4w12-vacant` | 11 (slot 12 empty) | 11 | 3× | exact |  | [4way/v12_vacant.toml](4way/v12_vacant.toml) |
| `4w12-x2` | 12 | 22 | 6× | exact |  | [4way/v12_x2.toml](4way/v12_x2.toml) |
| `4w12-oil` | 12 | 11 | 3× | 1 bowler(s) off | 2+3+3+3 (27 repeats) | [4way/v12_oil.toml](4way/v12_oil.toml) |
| `4w16` | 16 | 5 | 1× | 12 bowler(s) off |  | [4way/v16.toml](4way/v16.toml) |
| `4w16-vacant` | 15 (slot 16 empty) | 5 | 1× | 3 bowler(s) off |  | [4way/v16_vacant.toml](4way/v16_vacant.toml) |
| `4w16-x2` | 16 | 10 | 2× | exact | 5+5 | [4way/v16_x2.toml](4way/v16_x2.toml) |
| `4w20` | 20 | 19 | 3× | exact |  | [4way/v20.toml](4way/v20.toml) |
| `4w20-vacant` | 19 (slot 20 empty) | 19 | 3× | exact |  | [4way/v20_vacant.toml](4way/v20_vacant.toml) |
| `4w20-x2` | 20 | 38 | 6× | exact |  | [4way/v20_x2.toml](4way/v20_x2.toml) |
| `4w20-oil` | 20 | 19 | 3× | exact | 5+4+5+5 | [4way/v20_oil.toml](4way/v20_oil.toml) |
| `4w24` | 24 | 23 | 3× | exact |  | [4way/v24.toml](4way/v24.toml) |
| `4w24-vacant` | 23 (slot 24 empty) | 23 | 3× | exact |  | [4way/v24_vacant.toml](4way/v24_vacant.toml) |
| `4w24-x2` | 24 | 46 | 6× | exact | 3+2+1+1+1+1+1+1+3+1+3+5+6+5+6+6 | [4way/v24_x2.toml](4way/v24_x2.toml) |
| `4w24-oil` | 24 | 23 | 3× | exact | 6+5+6+6 | [4way/v24_oil.toml](4way/v24_oil.toml) |
| `4w24-oil-x2` | 24 | 46 | 6× | exact | 6+5+6+6+6+5+6+6 | [4way/v24_oil_x2.toml](4way/v24_oil_x2.toml) |
| `4w28` | 28 | 9 | 1× | exact |  | [4way/v28.toml](4way/v28.toml) |
| `4w28-vacant` | 27 (slot 28 empty) | 9 | 1× | exact |  | [4way/v28_vacant.toml](4way/v28_vacant.toml) |
| `4w28-x2` | 28 | 18 | 2× | exact | 9+9 | [4way/v28_x2.toml](4way/v28_x2.toml) |
| `4w32` | 32 | 31 | 3× | exact |  | [4way/v32.toml](4way/v32.toml) |
| `4w32-vacant` | 31 (slot 32 empty) | 31 | 3× | exact |  | [4way/v32_vacant.toml](4way/v32_vacant.toml) |
| `4w32-x2` | 32 | 62 | 6× | exact |  | [4way/v32_x2.toml](4way/v32_x2.toml) |
| `4w32-oil` | 32 | 31 | 3× | exact | 8+7+8+8 | [4way/v32_oil.toml](4way/v32_oil.toml) |
| `4w32-oil-x2` | 32 | 62 | 6× | exact | 8+7+8+8+8+7+8+8 | [4way/v32_oil_x2.toml](4way/v32_oil_x2.toml) |
| `4w36` | 36 | 35 | 3× | exact |  | [4way/v36.toml](4way/v36.toml) |
| `4w36-vacant` | 35 (slot 36 empty) | 35 | 3× | exact |  | [4way/v36_vacant.toml](4way/v36_vacant.toml) |
| `4w36-x2` | 36 | 70 | 6× | exact | 3+1+1+1+2+1+2+2+1+1+1+2+1+1+1+1+1+1+1+1+2+1+1+1+1+3+9+9+9+8 | [4way/v36_x2.toml](4way/v36_x2.toml) |
| `4w36-oil` | 36 | 35 | 3× | exact | 9+9+9+8 | [4way/v36_oil.toml](4way/v36_oil.toml) |
| `4w36-oil-x2` | 36 | 70 | 6× | exact | 9+9+9+8+9+9+9+8 | [4way/v36_oil_x2.toml](4way/v36_oil_x2.toml) |
| `4w40` | 40 | 13 | 1× | exact |  | [4way/v40.toml](4way/v40.toml) |
| `4w40-vacant` | 39 (slot 40 empty) | 13 | 1× | exact |  | [4way/v40_vacant.toml](4way/v40_vacant.toml) |
| `4w40-x2` | 40 | 26 | 2× | exact | 13+13 | [4way/v40_x2.toml](4way/v40_x2.toml) |
| `hy11-4-3-0` | 11 | 7 | 1× | exact | 3 weeks 3-way, 4 weeks 2-way | [hybrid/files/v11_4-3-0_mixed.json](hybrid/files/v11_4-3-0_mixed.json) |
| `hy12-0-4-1` | 12 | 5 | 1× | exact | 4 weeks 3-way, 1 week 4-way | [hybrid/files/v12_0-4-1.json](hybrid/files/v12_0-4-1.json) |
| `hy12-2-3-1` | 12 | 6 | 1× | exact | 3 weeks 3-way, 1 week 4-way, 2 weeks 2-way | [hybrid/files/v12_2-3-1.json](hybrid/files/v12_2-3-1.json) |
| `hy12-4-2-1` | 12 | 7 | 1× | exact | 2 weeks 3-way, 1 week 4-way, 4 weeks 2-way | [hybrid/files/v12_4-2-1.json](hybrid/files/v12_4-2-1.json) |
| `hy12-3-4-0` | 12 | 7 | 1× | exact | 4 weeks 3-way, 3 weeks 2-way | [hybrid/files/v12_3-4-0.json](hybrid/files/v12_3-4-0.json) |
| `hy12-5-3-0` | 12 | 8 | 1× | 1 bowler(s) off | 3 weeks 3-way, 5 weeks 2-way | [hybrid/files/v12_5-3-0.json](hybrid/files/v12_5-3-0.json) |
| `hy12-6-1-1` | 12 | 8 | 1× | 1 bowler(s) off | 1 week 3-way, 1 week 4-way, 6 weeks 2-way | [hybrid/files/v12_6-1-1.json](hybrid/files/v12_6-1-1.json) |
| `hy12-7-2-0` | 12 | 9 | 1× | exact | 2 weeks 3-way, 7 weeks 2-way | [hybrid/files/v12_7-2-0.json](hybrid/files/v12_7-2-0.json) |
| `hy12-8-0-1` | 12 | 9 | 1× | exact | 1 week 4-way, 8 weeks 2-way | [hybrid/files/v12_8-0-1.json](hybrid/files/v12_8-0-1.json) |
| `hy12-9-1-0` | 12 | 10 | 1× | exact | 1 week 3-way, 9 weeks 2-way | [hybrid/files/v12_9-1-0.json](hybrid/files/v12_9-1-0.json) |
| `hy13-6-3-0` | 13 | 9 | 1× | exact | 3 weeks 3-way, 6 weeks 2-way | [hybrid/files/v13_6-3-0_mixed.json](hybrid/files/v13_6-3-0_mixed.json) |
| `hy14-7-0-2` | 14 | 9 | 1× | exact | 2 weeks 4-way, 7 weeks 2-way | [hybrid/files/v14_7-0-2_mixed.json](hybrid/files/v14_7-0-2_mixed.json) |
| `hy15-0-1-4` | 15 | 5 | 1× | 3 bowler(s) off | 1 week 3-way, 4 weeks 4-way | [hybrid/files/v15_0-1-4_mixed.json](hybrid/files/v15_0-1-4_mixed.json) |
| `hy15-4-5-0` | 15 | 9 | 1× | exact | 5 weeks 3-way, 4 weeks 2-way | [hybrid/files/v15_4-5-0_mixed.json](hybrid/files/v15_4-5-0_mixed.json) |
| `hy16-0-3-3` | 16 | 6 | 1× | exact | 3 weeks 3-way, 3 weeks 4-way | [hybrid/files/v16_0-3-3_mixed.json](hybrid/files/v16_0-3-3_mixed.json) |
| `hy16-3-0-4` | 16 | 7 | 1× | 3 bowler(s) off | 4 weeks 4-way, 3 weeks 2-way | [hybrid/files/v16_3-0-4.json](hybrid/files/v16_3-0-4.json) |
| `hy16-6-0-3` | 16 | 9 | 1× | exact | 3 weeks 4-way, 6 weeks 2-way | [hybrid/files/v16_6-0-3.json](hybrid/files/v16_6-0-3.json) |
| `hy16-9-0-2` | 16 | 11 | 1× | exact | 2 weeks 4-way, 9 weeks 2-way | [hybrid/files/v16_9-0-2.json](hybrid/files/v16_9-0-2.json) |
| `hy16-12-0-1` | 16 | 13 | 1× | exact | 1 week 4-way, 12 weeks 2-way | [hybrid/files/v16_12-0-1.json](hybrid/files/v16_12-0-1.json) |
| `hy17-4-6-0` | 17 | 10 | 1× | exact | 6 weeks 3-way, 4 weeks 2-way | [hybrid/files/v17_4-6-0_mixed.json](hybrid/files/v17_4-6-0_mixed.json) |
| `hy18-1-8-0` | 18 | 9 | 1× | exact | 8 weeks 3-way, 1 week 2-way | [hybrid/files/v18_1-8-0.json](hybrid/files/v18_1-8-0.json) |
| `hy18-3-7-0` | 18 | 10 | 1× | exact | 7 weeks 3-way, 3 weeks 2-way | [hybrid/files/v18_3-7-0.json](hybrid/files/v18_3-7-0.json) |
| `hy18-5-6-0` | 18 | 11 | 1× | exact | 6 weeks 3-way, 5 weeks 2-way | [hybrid/files/v18_5-6-0.json](hybrid/files/v18_5-6-0.json) |
| `hy18-7-5-0` | 18 | 12 | 1× | 1 bowler(s) off | 5 weeks 3-way, 7 weeks 2-way | [hybrid/files/v18_7-5-0.json](hybrid/files/v18_7-5-0.json) |
| `hy18-9-4-0` | 18 | 13 | 1× | exact | 4 weeks 3-way, 9 weeks 2-way | [hybrid/files/v18_9-4-0.json](hybrid/files/v18_9-4-0.json) |
| `hy18-11-3-0` | 18 | 14 | 1× | exact | 3 weeks 3-way, 11 weeks 2-way | [hybrid/files/v18_11-3-0.json](hybrid/files/v18_11-3-0.json) |
| `hy19-6-6-0` | 19 | 12 | 1× | exact | 6 weeks 3-way, 6 weeks 2-way | [hybrid/files/v19_6-6-0_mixed.json](hybrid/files/v19_6-6-0_mixed.json) |
| `hy20-4-0-5` | 20 | 9 | 1× | exact | 5 weeks 4-way, 4 weeks 2-way | [hybrid/files/v20_4-0-5.json](hybrid/files/v20_4-0-5.json) |
| `hy20-7-0-4` | 20 | 11 | 1× | exact | 4 weeks 4-way, 7 weeks 2-way | [hybrid/files/v20_7-0-4.json](hybrid/files/v20_7-0-4.json) |
| `hy20-10-0-3` | 20 | 13 | 1× | exact | 3 weeks 4-way, 10 weeks 2-way | [hybrid/files/v20_10-0-3.json](hybrid/files/v20_10-0-3.json) |
| `hy21-2-3-4` | 21 | 9 | 1× | 4 bowler(s) off | 3 weeks 3-way, 4 weeks 4-way, 2 weeks 2-way | [hybrid/files/v21_2-3-4_mixed.json](hybrid/files/v21_2-3-4_mixed.json) |
| `hy21-6-7-0` | 21 | 13 | 1× | exact | 7 weeks 3-way, 6 weeks 2-way | [hybrid/files/v21_6-7-0_mixed.json](hybrid/files/v21_6-7-0_mixed.json) |
| `hy22-3-0-6` | 22 | 9 | 1× | exact | 6 weeks 4-way, 3 weeks 2-way | [hybrid/files/v22_3-0-6_mixed.json](hybrid/files/v22_3-0-6_mixed.json) |
| `hy22-9-3-2` | 22 | 14 | 1× | exact | 3 weeks 3-way, 2 weeks 4-way, 9 weeks 2-way | [hybrid/files/v22_9-3-2_mixed.json](hybrid/files/v22_9-3-2_mixed.json) |
| `hy23-4-3-4` | 23 | 11 | 1× | exact | 3 weeks 3-way, 4 weeks 4-way, 4 weeks 2-way | [hybrid/files/v23_4-3-4_mixed.json](hybrid/files/v23_4-3-4_mixed.json) |
| `hy23-4-9-0` | 23 | 13 | 1× | exact | 9 weeks 3-way, 4 weeks 2-way | [hybrid/files/v23_4-9-0_mixed.json](hybrid/files/v23_4-9-0_mixed.json) |
| `hy24-0-1-7` | 24 | 8 | 1× | 12 bowler(s) off | 1 week 3-way, 7 weeks 4-way | [hybrid/files/v24_0-1-7.json](hybrid/files/v24_0-1-7.json) |
| `hy24-0-4-5` | 24 | 9 | 1× | exact | 4 weeks 3-way, 5 weeks 4-way | [hybrid/files/v24_0-4-5.json](hybrid/files/v24_0-4-5.json) |
| `hy24-2-3-5` | 24 | 10 | 1× | exact | 3 weeks 3-way, 5 weeks 4-way, 2 weeks 2-way | [hybrid/files/v24_2-3-5.json](hybrid/files/v24_2-3-5.json) |
| `hy24-0-7-3` | 24 | 10 | 1× | 1 bowler(s) off | 7 weeks 3-way, 3 weeks 4-way | [hybrid/files/v24_0-7-3.json](hybrid/files/v24_0-7-3.json) |
| `hy24-3-1-6` | 24 | 10 | 1× | exact | 1 week 3-way, 6 weeks 4-way, 3 weeks 2-way | [hybrid/files/v24_3-1-6.json](hybrid/files/v24_3-1-6.json) |
| `hy24-1-5-4` | 24 | 10 | 1× | exact | 5 weeks 3-way, 4 weeks 4-way, 1 week 2-way | [hybrid/files/v24_1-5-4.json](hybrid/files/v24_1-5-4.json) |
| `hy24-1-8-2` | 24 | 11 | 1× | exact | 8 weeks 3-way, 2 weeks 4-way, 1 week 2-way | [hybrid/files/v24_1-8-2.json](hybrid/files/v24_1-8-2.json) |
| `hy24-5-0-6` | 24 | 11 | 1× | exact | 6 weeks 4-way, 5 weeks 2-way | [hybrid/files/v24_5-0-6.json](hybrid/files/v24_5-0-6.json) |
| `hy24-0-10-1` | 24 | 11 | 1× | exact | 10 weeks 3-way, 1 week 4-way | [hybrid/files/v24_0-10-1.json](hybrid/files/v24_0-10-1.json) |
| `hy24-2-6-3` | 24 | 11 | 1× | exact | 6 weeks 3-way, 3 weeks 4-way, 2 weeks 2-way | [hybrid/files/v24_2-6-3.json](hybrid/files/v24_2-6-3.json) |
| `hy24-4-2-5` | 24 | 11 | 1× | exact | 2 weeks 3-way, 5 weeks 4-way, 4 weeks 2-way | [hybrid/files/v24_4-2-5.json](hybrid/files/v24_4-2-5.json) |
| `hy24-3-4-4` | 24 | 11 | 1× | exact | 4 weeks 3-way, 4 weeks 4-way, 3 weeks 2-way | [hybrid/files/v24_3-4-4.json](hybrid/files/v24_3-4-4.json) |
| `hy24-3-7-2` | 24 | 12 | 1× | exact | 7 weeks 3-way, 2 weeks 4-way, 3 weeks 2-way | [hybrid/files/v24_3-7-2.json](hybrid/files/v24_3-7-2.json) |
| `hy24-1-11-0` | 24 | 12 | 1× | exact | 11 weeks 3-way, 1 week 2-way | [hybrid/files/v24_1-11-0.json](hybrid/files/v24_1-11-0.json) |
| `hy24-5-3-4` | 24 | 12 | 1× | exact | 3 weeks 3-way, 4 weeks 4-way, 5 weeks 2-way | [hybrid/files/v24_5-3-4.json](hybrid/files/v24_5-3-4.json) |
| `hy24-4-5-3` | 24 | 12 | 1× | exact | 5 weeks 3-way, 3 weeks 4-way, 4 weeks 2-way | [hybrid/files/v24_4-5-3.json](hybrid/files/v24_4-5-3.json) |
| `hy24-2-9-1` | 24 | 12 | 1× | exact | 9 weeks 3-way, 1 week 4-way, 2 weeks 2-way | [hybrid/files/v24_2-9-1.json](hybrid/files/v24_2-9-1.json) |
| `hy24-6-1-5` | 24 | 12 | 1× | exact | 1 week 3-way, 5 weeks 4-way, 6 weeks 2-way | [hybrid/files/v24_6-1-5.json](hybrid/files/v24_6-1-5.json) |
| `hy24-4-8-1` | 24 | 13 | 1× | exact | 8 weeks 3-way, 1 week 4-way, 4 weeks 2-way | [hybrid/files/v24_4-8-1.json](hybrid/files/v24_4-8-1.json) |
| `hy24-6-4-3` | 24 | 13 | 1× | exact | 4 weeks 3-way, 3 weeks 4-way, 6 weeks 2-way | [hybrid/files/v24_6-4-3.json](hybrid/files/v24_6-4-3.json) |
| `hy24-3-10-0` | 24 | 13 | 1× | exact | 10 weeks 3-way, 3 weeks 2-way | [hybrid/files/v24_3-10-0.json](hybrid/files/v24_3-10-0.json) |
| `hy24-7-2-4` | 24 | 13 | 1× | exact | 2 weeks 3-way, 4 weeks 4-way, 7 weeks 2-way | [hybrid/files/v24_7-2-4.json](hybrid/files/v24_7-2-4.json) |
| `hy24-8-0-5` | 24 | 13 | 1× | exact | 5 weeks 4-way, 8 weeks 2-way | [hybrid/files/v24_8-0-5.json](hybrid/files/v24_8-0-5.json) |
| `hy24-5-6-2` | 24 | 13 | 1× | exact | 6 weeks 3-way, 2 weeks 4-way, 5 weeks 2-way | [hybrid/files/v24_5-6-2.json](hybrid/files/v24_5-6-2.json) |
| `hy24-9-1-4` | 24 | 14 | 1× | exact | 1 week 3-way, 4 weeks 4-way, 9 weeks 2-way | [hybrid/files/v24_9-1-4.json](hybrid/files/v24_9-1-4.json) |
| `hy24-6-7-1` | 24 | 14 | 1× | exact | 7 weeks 3-way, 1 week 4-way, 6 weeks 2-way | [hybrid/files/v24_6-7-1.json](hybrid/files/v24_6-7-1.json) |
| `hy24-8-3-3` | 24 | 14 | 1× | exact | 3 weeks 3-way, 3 weeks 4-way, 8 weeks 2-way | [hybrid/files/v24_8-3-3.json](hybrid/files/v24_8-3-3.json) |
| `hy24-5-9-0` | 24 | 14 | 1× | exact | 9 weeks 3-way, 5 weeks 2-way | [hybrid/files/v24_5-9-0.json](hybrid/files/v24_5-9-0.json) |
| `hy24-7-5-2` | 24 | 14 | 1× | exact | 5 weeks 3-way, 2 weeks 4-way, 7 weeks 2-way | [hybrid/files/v24_7-5-2.json](hybrid/files/v24_7-5-2.json) |
| `hy25-6-3-4` | 25 | 13 | 1× | exact | 3 weeks 3-way, 4 weeks 4-way, 6 weeks 2-way | [hybrid/files/v25_6-3-4_mixed.json](hybrid/files/v25_6-3-4_mixed.json) |
| `hy26-7-3-4` | 26 | 14 | 1× | exact | 3 weeks 3-way, 4 weeks 4-way, 7 weeks 2-way | [hybrid/files/v26_7-3-4_mixed.json](hybrid/files/v26_7-3-4_mixed.json) |
| `hy27-6-4-4` | 27 | 14 | 1× | exact | 4 weeks 3-way, 4 weeks 4-way, 6 weeks 2-way | [hybrid/files/v27_6-4-4_mixed.json](hybrid/files/v27_6-4-4_mixed.json) |
| `hy28-3-0-8` | 28 | 11 | 1× | exact | 8 weeks 4-way, 3 weeks 2-way | [hybrid/files/v28_3-0-8.json](hybrid/files/v28_3-0-8.json) |
| `hy28-6-0-7` | 28 | 13 | 1× | 1 bowler(s) off | 7 weeks 4-way, 6 weeks 2-way | [hybrid/files/v28_6-0-7.json](hybrid/files/v28_6-0-7.json) |
| `hy29-4-6-4` | 29 | 14 | 1× | exact | 6 weeks 3-way, 4 weeks 4-way, 4 weeks 2-way | [hybrid/files/v29_4-6-4_mixed.json](hybrid/files/v29_4-6-4_mixed.json) |
| `hy30-1-14-0` | 30 | 15 | 1× | exact | 14 weeks 3-way, 1 week 2-way | [hybrid/files/v30_1-14-0.json](hybrid/files/v30_1-14-0.json) |
| `hy31-6-6-4` | 31 | 16 | 1× | exact | 6 weeks 3-way, 4 weeks 4-way, 6 weeks 2-way | [hybrid/files/v31_6-6-4_mixed.json](hybrid/files/v31_6-6-4_mixed.json) |
| `hy32-1-0-10` | 32 | 11 | 1× | exact | 10 weeks 4-way, 1 week 2-way | [hybrid/files/v32_1-0-10.json](hybrid/files/v32_1-0-10.json) |
| `hy32-4-0-9` | 32 | 13 | 1× | exact | 9 weeks 4-way, 4 weeks 2-way | [hybrid/files/v32_4-0-9.json](hybrid/files/v32_4-0-9.json) |
| `hy35-4-3-8` | 35 | 15 | 1× | exact | 3 weeks 3-way, 8 weeks 4-way, 4 weeks 2-way | [hybrid/files/v35_4-3-8_mixed.json](hybrid/files/v35_4-3-8_mixed.json) |
| `hy36-0-1-11` | 36 | 12 | 1× | 19 bowler(s) off | 1 week 3-way, 11 weeks 4-way | [hybrid/files/v36_0-1-11.json](hybrid/files/v36_0-1-11.json) |
| `hy36-2-0-11` | 36 | 13 | 1× | exact | 11 weeks 4-way, 2 weeks 2-way | [hybrid/files/v36_2-0-11.json](hybrid/files/v36_2-0-11.json) |
| `hy36-0-4-9` | 36 | 13 | 1× | exact | 4 weeks 3-way, 9 weeks 4-way | [hybrid/files/v36_0-4-9.json](hybrid/files/v36_0-4-9.json) |
| `hy36-1-2-10` | 36 | 13 | 1× | 11 bowler(s) off | 2 weeks 3-way, 10 weeks 4-way, 1 week 2-way | [hybrid/files/v36_1-2-10.json](hybrid/files/v36_1-2-10.json) |
| `hy36-1-5-8` | 36 | 14 | 1× | 5 bowler(s) off | 5 weeks 3-way, 8 weeks 4-way, 1 week 2-way | [hybrid/files/v36_1-5-8.json](hybrid/files/v36_1-5-8.json) |
| `hy36-3-1-10` | 36 | 14 | 1× | 1 bowler(s) off | 1 week 3-way, 10 weeks 4-way, 3 weeks 2-way | [hybrid/files/v36_3-1-10.json](hybrid/files/v36_3-1-10.json) |
| `hy36-2-3-9` | 36 | 14 | 1× | 3 bowler(s) off | 3 weeks 3-way, 9 weeks 4-way, 2 weeks 2-way | [hybrid/files/v36_2-3-9.json](hybrid/files/v36_2-3-9.json) |
| `hy36-0-7-7` | 36 | 14 | 1× | 7 bowler(s) off | 7 weeks 3-way, 7 weeks 4-way | [hybrid/files/v36_0-7-7.json](hybrid/files/v36_0-7-7.json) |
| `hy36-1-17-0` | 36 | 18 | 1× | exact | 17 weeks 3-way, 1 week 2-way | [hybrid/files/v36_1-17-0.json](hybrid/files/v36_1-17-0.json) |
| `hy40-3-0-12` | 40 | 15 | 1× | exact | 12 weeks 4-way, 3 weeks 2-way | [hybrid/files/v40_3-0-12.json](hybrid/files/v40_3-0-12.json) |
<!-- catalogue:end -->

## How they were made
- **One meeting per couple (KTS, affine plane, (28,4,1)):** classical resolvable designs.
- **Two or three meetings per couple:** 1-rotational designs over Z_(N−1) ∪ {∞}, also called the extended circle method. Keeping base group j on lane pair j balances everyone except ∞, which is why the `_vacant` files work.
- **Exact lane balance for the single rounds of 20 and 24 (4-way) and 24 and 27 (3-way):** designs with a symmetry that also rotates the lane pairs, for example Z_5 × 4 classes for 20.
- **Positions:** equitable bipartite edge-colouring (`tools/positions.py`).

Run `python3 verify.py` to re-check everything from the weeks alone. The search code is in each folder's `tools/`.

## Rebuilding the pages
`python3 tools/build_pages.py` recomputes every figure from the weeks and rewrites `docs/` (the page, the
methods HTML via pandoc, and `schedules.json`) and the catalogue above. `--site DIR` also copies the three
files into a website folder. `docs/` is ready for GitHub Pages (Settings → Pages → branch `main`, folder `/docs`).

[METHODS.md](METHODS.md) has the full account: how each design was built, every lane-balance approach that was tried and failed, the impossibility proofs, the two-round and vacancy methods, the limits on short seasons, and what's still open.

## Licence
CC0 1.0 (public domain): use, copy and adapt the schedules and code freely, no attribution required. See [LICENSE](LICENSE).
