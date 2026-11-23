# 4-way 24 in four oil blocks (6+6+6+5), lane-exact — found 24 Nov 2026

Result: `4way/v24_oil.json/.toml` — resolvable 2-(24,4,3), 23 distinct weeks, 4 clash-free contiguous blocks
(file order 6+5+6+6), lane pairs exact (every bowler 3 or 4 times on each), worst prefix spread 2, positions
by `positions.assign`. `python3 verify.py` prints ALL OK. The old 8-block file is `previous_v24_oil.json`.

## Construction
Points p = 4a+u: a in 0..5 ("super-point"), u in Z2^2 (xor). N = Z2^2 acts on u; sigma: a -> (0 1 2)(3 4 5), u fixed.
- N fixes every oil block. Each week is either fixed by all of N (types R+H, R+F+F, H+H+F+F, H+H+H; 11,580
  weeks, `pool.py`) or is one of a pair {W, t_j W} with W fixed by one involution t_i (368,640 pairs by class
  set, `pool2.py`). So a week's couples are whole N-classes: 60 cross classes (a,b,d), 4 couples each, and 18
  inner classes (a,i), 2 couples each. The design is an exact cover: every class in exactly 3 of 4 blocks.
- sigma cycles blocks 1->2->3, so only block A (weight 6) and block D (weight 5) are searched: A must cover
  >= 2 classes of every sigma-orbit; D covers exactly the classes not covered three times.
- `sigsearch.c`: DFS over A with forced classes; D by exact cover. 62 designs from 17/4000 of the root (~1.5 min
  each on one core). None of these had usable lanes (below).
- For lanes, D was restricted to sigma-invariant weeks (`dpool.py`: 648 class sets), and `asearch.c` finds A for
  a given D. 6 of the first ~110 class sets gave solutions within 25 s; 97 designs rebuilt (`rebuild2.py`).
- Lanes (`lanes_eq.c`): sigma rotates the lane pairs in two tracks (0 1 2)(3 4 5); block 2/3 = rotated block 1,
  each D week has lane(sigma g) = pi(lane g). Annealing over 720^6 x 18^5: design eq_16 exact at restart 17
  (20M steps each); the other 96 designs were not tried to completion.
- Prefix spread <= 2 holds for ANY week order: the four leaves are disjoint, so after two whole blocks every
  couple has met, and after three every couple has met twice.
- `finish_v3.py` re-verifies from the weeks alone, orders, assigns positions, writes the files.

## What failed (in order tried)
- Unsymmetric annealing over 23 weeks (`sa.c` mode 0): cost 92-130. Even one 6-week block (social golfer
  6-4-6) is not solved in a minute (mode 2, best 1).
- Z3 cycling three blocks, A and D free (`sa.c` mode 1): 72.
- Z3 fixing all blocks, base weeks + invariant weeks (`sax.c`): 10-24.
- Z6 = sigma x tau with tau-invariant weeks (`sa6.c`): 20-44.
- All 23 weeks N-invariant: exhaustive with sigma (`cliqs.c`, both sigma variants): 1,470,560 six-week blocks,
  none passes. Without sigma (`combo.c`) stopped at ~3% of blocks as first block: 0 triples (not exhaustive).
- z3 / dancing links on the N-invariant pool (`z3pool.py`, `dlx.c`): no answer; DLX's MRV picks the wrong items.
- Lanes on the first 62 designs: plain annealing 5-8 cells off (`lanes.c`), z3 unknown after 200 s and still
  running at ~10 min when stopped, sigma-rotated lanes with a free D 6+ off (`lanes_sym.c`). No lane assignment
  equivariant under N exists for any N-action on the 6 lane pairs (inner-class counting, per type).

## Reproduce
    python3 pool2.py out/pool2 && python3 mksig2.py out/pool2 && python3 dpool.py out/pool2 0 out/dcand_0.txt
    cc -O3 -o asearch asearch.c; cc -O3 -o lanes_eq lanes_eq.c -lm      (mkdir out first)
    ./runx.sh 0 keep/dx_sig0.txt 0 1 25 > out/runx0_0.log ; python3 rebuild2.py out/pool2 0 out/runx0_*.log
    ./lanes_eq out/eq_16.txt design_eq16_lanes.txt 3 20 0.7 0.1 30 0 ; python3 finish_v3.py --write
Kept: `design_eq16*.{txt,json}` (0-based points; blocks A, sA, ssA, D), `keep/` (found lists, D class sets).
