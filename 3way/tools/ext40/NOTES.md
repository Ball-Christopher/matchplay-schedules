# 3-way 30 / 33 / 36 / 39: search notes (24 November 2026)

Every file passes `python3 verify.py` (ALL OK). All 14 files have exact lane pairs. Positions come from
`positions.assign`, and week order from `schedlib.order_weeks` (3 restarts, best worst-spread kept).

## Code
| File | What it does |
|---|---|
| `zn.c` | Z_n × 3 lane-rotating design (generalises `fable_search/z8.c`, `z9.c`). `zn n B I lam R seed`. Base weeks by simulated annealing on pair-orbit counts (the old randomised DFS was too slow from n = 10 up); invariant trios random. With R=2 it finds two designs together: no shared trio orbit, each round lane-exact alone and the pair exact over both rounds. |
| `zm.c` | Z_m × C classes with T = C/3 tracks of m lane pairs. The shift rotates every track. Joint annealing over the base weeks **and** the invariant weeks (this joint move set was what made 30 work). Optional orbit-level block penalty (`BLK`). |
| `zo.c` | Oil versions, built in independent *parts* whose orbit budgets force the block conditions: `oil36b` (used), `oil30b` (used), plus `oil36` and `oil30`, which are kept as the failed variants below. |
| `zb.c` | A pair-level block-penalty annealer. It failed (below) and is kept for the record. |
| `finish.py` | Turns search output into the library files: `main N file [classes]`, `vacant N`, `oil N file`. It writes JSON/TOML in the existing formats. `vacant` contains the 1-rotational Z_(v−1) ∪ ∞ search. |
| `out/` | The search outputs the files were built from (weeks plus BASE/INV design data). |

Binaries `zn zm zo zb` were added to `.gitignore`. Build with `cc -O2 -o X X.c -lm`.

## Results
| File | Construction | Search time | Lanes | Blocks | Worst prefix spread | x2 repeats |
|---|---|---|---|---|---|---|
| v30 | Z_5 × 6 classes, 2 tracks of 5. 4 base weeks × 5 + 9 invariant weeks (two transversal orbits each, one per track) | ~30 s (`zm 5 6 4 9 2 1 1`) | exact | – | 2 (21 of 28 prefixes) | – |
| v30_vacant | 1-rotational Z_29 ∪ ∞, base group j on lane pair j | seconds | exact (short group always on lane pair 1) | – | 2 | – |
| v30_x2 | round 1 = v30. Round 2 by `schedlib.second_round` (best of 20 × 2000 tries) | ~30 s | exact | – | 2 | **5** |
| v30_oil | Z_5 × 6, 4 base + 9 invariant weeks in parts (below) | ~45 s (`zo oil30b 3`) | exact | **3** [14, 9, 6] (lower bound) | 2 (week 15 only) | – |
| v33 | KTS(33) on Z_11 × 3: 1 base week × 11 + 5 invariant weeks | < 5 s (`zn 11 1 5 1 2 1`) | exact | – | 1 | – |
| v33_vacant | v33 with slot 33 empty. Already exact for everyone, so the short group moves round the lane pairs | – | exact | – | 1 | – |
| v33_x2 | pair of KTS(33) found together, no shared trio orbit, `oil_blocks` [16, 16] | < 5 s | exact | 2 | 1 | **0** |
| v36 | Z_12 × 3: 2 base weeks × 12 + 11 invariant weeks | ~20 s (`zn 12 2 11 2 2 2`, round 1) | exact | – | 2 (28 of 34) | – |
| v36_vacant | 1-rotational Z_35 ∪ ∞ | seconds | exact (short group on lane pair 1) | – | 2 | – |
| v36_x2 | the same pair search, round 2 a second Z_12 design with no shared trio orbit | ~20 s | exact | – | 2 | **0** |
| v36_oil | Z_12 × 3 in parts (below) | < 60 s, first try (`zo oil36b 1`) | exact | **3** [16, 10, 9] (lower bound) | 2 (weeks 17–23) | – |
| v39 | KTS(39) on Z_13 × 3: 1 base week × 13 + 6 invariant weeks | < 5 s (`zn 13 1 6 1 2 1`) | exact | – | 1 | – |
| v39_vacant | v39 with slot 39 empty (as for 33) | – | exact | – | 1 | – |
| v39_x2 | KTS(39) pair, `oil_blocks` [19, 19] | < 5 s | exact | 2 | 1 | **0** |

No file has a trio repeated within a round. The total compute was about 60 minutes of wall time, mostly
the failed attempts below. Every successful search took under a minute.

## Constructions worth knowing
- **Parity obstruction: Z_10 × 3 cannot give 30 (λ = 2).** Map Z_10 → Z_2. Each trio has 0 or 2 pairs
  with odd difference, and so does each invariant week (it is transversal, since 3 ∤ 10). Within one class,
  the odd pure differences 1, 3 (twice each) and 5 (the short orbit, once) make 5 per class, 15 in all. The
  mixed odd differences give 30 minus the invariant weeks' even share. That leaves an odd total for the base
  weeks, which can only supply an even one. The annealer stuck at cost 2 every time, as this predicts.
  Hence Z_5 × 6 with 2 lane tracks for 30. Z_12 × 3 for 36 is fine, because 3 + 3 + 3 + 0 is even.
- **v36_oil.** v24's split (block 1 = one whole development plus 5 invariant weeks, 17 weeks, leaving the
  antipodal 1-factor) is impossible for Z_12 by the same parity count (that block needs 27 odd orbits). This
  was confirmed: `zo oil36` never got that part below cost 2. The working split is 16 + 10 + 9:
  - Block 1 = P0..P11 + 4 invariant weeks. Each orbit is used at most once, leaving the 3 antipodal orbits
    and a triangle M of mixed orbits (0,1,d1)(0,2,d2)(1,2,d3), with d1 + d2 + d3 odd so the parity works.
  - Q0 + 7 invariant weeks use every orbit once, the antipodal ones included, and M twice. An M orbit may be
    used twice only at Q0 offsets 6 apart, or once in an invariant week of each later block (a penalty term).
  - Block 2 = Q0..Q5 + 4 invariant weeks. Block 3 = Q6..Q11 + 3.
- **v30_oil.** Z_5 is odd, so there is no half-development trick. Block 1 = 2 base weeks + 4 invariant weeks
  (14 weeks): a Z_5-invariant NKTS(30) missing a 1-factor F of 3 mixed orbits on the class pairing
  {0,1}{2,3}{4,5}. The other part is 2 base weeks + 5 invariant weeks covering every orbit once and F twice,
  with F at most once per block (orbit-level penalty). Block 2 = base week 3 + 4 invariant weeks (9), and
  block 3 = base week 4 + 1 invariant week (6).
- **Lanes** were never the problem once the symmetry rotated the lanes. The (track, lane − x) residue DFS
  succeeded on the first or second design every time, apart from the joint two-round 30 case below.

## What failed
- `zn` with the z8-style randomised DFS on n = 10 and 12 (minutes, nothing). Annealing replaced it.
- `zn 10 2 9 2`: always stuck at cost 2. This is the parity obstruction above.
- `zm 5 6` with random invariant weeks and only the base weeks annealed: stuck at cost 4–12 over 20M–200M
  iterations, for every split B = 2..5. Annealing the invariant weeks as well fixed it in about 30 s.
- **Two-round pair for 30** (`zm 5 6 B I 2 2`). Pairs with no shared trio orbit were found (about 1 in 30),
  but the joint two-round lane DFS hit its 3M-node cap every time (12 attempts). So v30_x2 uses
  `second_round` and has 5 repeated trios. A round-by-round lane DFS, or a larger cap, would probably give
  0 repeats.
- Oil, orbit-level block penalty in one joint anneal (`zm` with `BLK`), for 30 (5+4 and 4+9 splits) and 36
  (the v24-style split): costs 7–22, never solved. For 36 this is the parity obstruction. For 30 the
  coupled problem was simply too hard for this annealer.
- `zo oil30` (14 + 10 + 5: 2 base + 4 invariant, then 3 base weeks with F twice): part 2 was solved only
  3 times in about 160 attempts, and those failed the trio-repeat or lane step. Moving invariant weeks into
  the second part (`oil30b`) made it easy.
- `zb` (pair-level block penalty): could not even redo 24's known [11, 6, 6] in 100 s (best cost 2).
  Abandoned in favour of the orbit-budget parts.

## Unresolved or could be better
- v30_x2: 5 repeated trios (v24_x2 has 4). See above for the likely fix.
- Prefix spread: v30 and v36 sit at 2 for most of the middle season (21 of 28 and 28 of 34 prefixes). This
  is unavoidable at some weeks for v ≡ 0 (mod 6), but the order was annealed only lightly (3 × 3000–4000
  steps of `order_weeks`). The oil files do better (2 at only week 15 for 30, and weeks 17–23 for 36).
- The vacancy files for 30 and 36 keep the short group on lane pair 1 every week, as in v12–v24.
