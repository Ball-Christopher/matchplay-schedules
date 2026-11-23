# 4-way 32 / 36 / 40: search notes (24 Nov 2026)

All 11 files pass `python3 verify.py` (ALL OK). Couples and positions are exact everywhere. Lanes are
exact in 7 of the 11 files.

| File | Weeks | Lanes | Oil blocks (repeats) | Worst prefix | x2 repeated groups |
|---|---|---|---|---|---|
| v32 | 31 | **13 bowlers off** (one lane pair 5×, target 3–4) | | 3 | |
| v32_vacant | 31 | exact | | 3 | |
| v32_x2 | 62 | exact | | 3 | 0 |
| v32_oil | 31 | **17 off** | **13** (3,4,2,2,2,2,2,3,2,2,2,2,3), 0 | 3 | |
| v36 | 35 | exact | | 3 | |
| v36_vacant | 35 | exact | | 3 | |
| v36_x2 | 70 | exact | | 3 | 0 |
| v36_oil | 35 | exact | **11** (4,3,3,3,3,3,3,3,3,3,4), 0 | 3 | |
| v40 | 13 | **2 off** | | 1 | |
| v40_vacant | 13 | **1 real bowler off** | | 1 | |
| v40_x2 | 26 | exact | [13, 13], 0 | 1 | 0 |

Unresolved, for a stronger pass: exact lanes for v32, v40 and v40_vacant, and the 4-block oil target for 32 and 36.

## Code (this folder)
- `zsym.c` is the main Z_m × 4 lane-rotating search. Usage: `zsym m NB NT NH lambda oil seed [designs] [iters] [T0] [Tend] [tabu] [tenure] [deep]`.
  - It uses NB base weeks developed mod m, NT transversal invariant weeks and NH "half" weeks (m even).
  - Stage 1 anneals pair-orbit counts. Stage 2 anneals the lanes per bowler.
  - Environment switches:
    - `PHI=k` ties the base weeks by the class map φ = (0)(1 2 3), with k φ-orbits of transversals.
    - `DUMP=2` prints designs without solving lanes.
    - `ACCEPT=c` prints the first lane solution with cost ≤ c.
    - `LTRY` and `LIT` set the lane-annealing effort.
- `lanes_z3.py`: exact z3 lane solve for zsym designs (rotating lanes).
- `res32.py`: the residue-level necessary condition for 32.
- `lanes_gen.py`: general z3 lane solve.
- `lanesa.c`: general lane annealer; `IGN=p` ignores one bowler.
- `rot1.c`: 1-rotational Z_(v−1) ∪ {∞} base weeks for the vacant files.
- `dfs13.c`: resolvable (40,4,1) on Z_13 × 3 ∪ {∞}. `PSI=3` imposes (a,i) → (a+1, 3i).
- `dfs40.c`: λ = 1 on Z_10 × 4 with 1 base, 2 transversal and 1 half week, with optional symmetry `sig mu tau`.
- `oilcolor.py`: exact colouring of the week clash graph. `chrom_cands.py` applies it to many designs.
- `finish.py` and `run32.py` / `run36.py` / `run40.py`: ordering, positions and output via `schedlib.write`.
- Raw designs: `p36.txt` (v36), `p32_best.txt` (v32), `lo36_11.json` (v36_oil), `oil32_lanes.json` (v32_oil), `r32.txt` / `r36.txt` (vacant base weeks), `b40m.txt` (240 Z_13 designs; v40 uses line 116), `w40_main.json`, `w40_vac.json`.

## 36: everything exact
- **Plain Z_9 × 4 does not anneal.** With 3 base weeks developed mod 9 and 8 transversal weeks, about 30 annealing runs and a tabu search all stalled at pair cost 2–6. A 2-move deep descent didn't help. Even the original `v20_z5_search.c` needs about 30 restarts for m = 5.
- **The fix: tie the three base weeks.** The class map φ: (a,i) → (φ(a), i), with φ = (0)(1 2 3), commutes with Z_m. Requiring base week w+1 = φ(base week w), with transversals in φ-orbits (here 2 orbits of 3 plus 2 φ-fixed weeks (0,c,c,c)), cuts the search by a factor of 3.
  - It solves m = 5 instantly. For m = 9 it finds a design in seconds (`PHI=2`). `PHI=0` and `PHI=1` stall at costs 30 and 12, because the transversal orbit structure matters.
  - The lanes are solved without φ (free lane permutations): 10 designs in 44 s, the last one exact on residues.
- **v36:** that design, with week order annealed. Worst prefix spread 3, the same as 20 and 24.
- **v36_vacant:** 1-rotational Z_35 ∪ {∞}, found by `rot1` in 0.1 s. Base group j is on lane pair j, so the 35 real bowlers are exact.
- **v36_x2:** `schedlib.second_round`. Exact, with 0 repeated groups at the first try.
- **v36_oil: 11 blocks, 0 repeats, exact lanes.**
  - The 4-block template (each base orbit clash-free, transversals as the fourth block: `zsym ... oil=1`, with PHI=2 or 1) never reached 0. The best penalty was 15, i.e. 5 same-block repeats, after about 12 runs of 7 minutes.
  - Fallback: the chromatic number of the week clash graph across 39 PHI designs ranges from 11 to 17. One of the 11s was lane-solved by z3 in seconds (`lanes_z3.py`) and split by its exact colouring.
  - The main v36 design itself needs 17 blocks.

## 32: pairs fine, lanes not exact
- **Antipodal pairs force a non-rotating week.** Z_8 has an involution, so a base week covering an antipodal pair {i, i+4} covers it twice. λ = 3 needs an odd count, so some Z_8-invariant week must contain groups {(x,t),(x,t+4),(y,b+t),(y,b+t+4)}, whose orbit has length 4. Such a "half" week can't rotate with the 8 lane pairs, because B and B+4 are the same group.
  - This is the same parity issue as the dead-end Z_6 × 4 for 24.
  - The used configuration is 3 base weeks (φ-tied), 4 transversal weeks and 3 half weeks (pairings {01|23}, {02|13}, {03|12}, also φ-tied).
  - Designs come instantly (`PHI=1`; about 3,800 were dumped). The alternative with 1 half week and 6 transversals can't be φ-tied, since the half week breaks φ-symmetry of the totals.
- **Lanes: a hard floor of 16.** Per-bowler lane annealing on more than 300 designs never went below a cost of 16, i.e. sixteen cells at 5. z3 on the full model returned unknown after 6 minutes. z3 on a residue-level necessary condition returned unknown after 20 s × 6. General annealing (`lanesa`) on this design, or on the 1-rotational design, reached 16–17.
  - **Necessary condition found by brute force:** each class's symmetric-part residue counts h[a][·] must be 4-periodic and of the form 3⁴4⁴ or 2²4⁶. This holds because bowlers u and u+4 always share a half-week lane pair.
  - This is very likely a structural obstruction for this configuration, but it is not proven.
  - A route to exact lanes needs a different group, for example lane pairs in two tracks of 4 rotated by Z_4 as in v24, or a non-symmetric lane solve with a stronger solver.
- **v32:** the cost-16 solution. 13 bowlers each have one lane pair 5 times instead of 4 and otherwise 3–4; nobody is further off.
  - Alternative not used: the 1-rotational design has only 1 bowler off, but that bowler (∞) sits on one lane pair all 31 weeks.
- **v32_vacant:** 1-rotational Z_31 ∪ {∞}, exact. **v32_x2:** `second_round` makes the two-round totals exact even though round 1 isn't, with 0 repeated groups.
- **v32_oil: 13 blocks, 0 repeats, 17 bowlers off on lanes.**
  - The 4-block template ([9,9,9,4]: each base orbit plus one half week, then the transversals) stalled at penalty 24 or more.
  - Fallback: the best of 60 designs by chromatic number (13), lanes by `lanesa` (20 excess cells), blocks from the exact colouring.

## 40: λ = 1, lanes not exact
- **Z_10 × 4 lane-rotating route (1 base, 2 transversal and 1 half week): no design found.**
  - Annealing stalled at cost 8. A plain DFS hit its node limits.
  - An exhaustive DFS under every order-4 symmetry (a,i) → (a+1, μi) with μ = 1, 3, 7, 9, and under (a+2, 3i), found no solution: about 1,000 invariant-week configurations, all exhausted.
  - Order-2 symmetries were too slow to finish (8 runs of 4 minutes or more).
- **Used: Z_13 × 3 ∪ {∞}** (the v28 analogue). The base week is also fixed by (a,i) → (a+1, 3i), with the ∞ group a ψ-orbit plus ∞, which makes the exact-cover DFS instant (`dfs13`, `PSI=3`). The plain DFS found nothing in 2 minutes.
- **Lanes:** Z_13 doesn't act on 10 lane pairs. `lanesa` over 240 designs reached a best of 2 excess cells (6 designs). z3 PB returned unknown after 280 s on 4 designs, and the 950 s runs on the 4 best designs were stopped unfinished.
  - **v40:** 2 bowlers off.
  - **v40_vacant** (∞ = player 40 = vacant, lanes re-annealed ignoring it): 1 real bowler off.
  - **v40_x2:** `second_round` gives exact totals, 0 repeated groups, and `oil_blocks` [13, 13].

## Compute used
About 2 hours of wall time, more than the 90 minutes asked for, mostly with 8–16 cores busy. The large items:
- 36 / 32 oil annealing: about 12 × 7 min.
- 32 lane attempts: z3 2 × 6 min, plus annealing.
- 40 symmetric DFS runs: about 10 × 2–4 min.
- 40 mass lane annealing: about 12 cores × 6 min.
