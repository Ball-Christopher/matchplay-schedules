# Astra results, third batch (24 November 2026)

Results produced by Astra (another AI agent) against repository revision `61eecc0`, then checked independently here. `START_HERE.md`, `METHODS.md`, `DRAW_TABLES.md`, the schedule files, `proofs/` and `inputs/` are Astra's handoff as received; its copy of our own scripts (`upstream/`) was left out. `check/` holds the independent checks written for this review. None of Astra's own scripts were run.

## How it was checked

- **Schedules:** the 36-in-trios two-round file was checked with `../astra-2026-11-24b/check/checkm.py`. That covers round 1 being identical to `3way/v36_oil`, λ, lanes and positions per round and overall, and greedy blocks. The hybrids were checked with the repository's `hybrid/verify.py`, and the qualifying draw was scored with `qualifying/model.py`. Each `inputs/` file was compared with the library file it copies; all six are identical.
- **`check/prefix_z3.py v20 v24 v36`:** a direct z3 model over week orders, without Astra's pivot reduction. It asks whether any order keeps every prefix at spread ≤ 2, i.e. no prefix holds all 3 meetings of one couple while missing all 3 of another. As a control, the same model finds such orders for `v20_oil` and `v24_oil`.
- **`check/grid36.py`:** a structural check, written independently of Astra's argument.
- **The 15-bowler symmetry search** was re-implemented twice from the method description alone, without reading Astra's code (`check/sym15/`).

## Outcome

| Claim | Checked result |
|---|---|
| **3-way 36, two rounds, oil first: 5 patterns (16+10+12+16+16)** | Confirmed. Round 1 identical to `3way/v36_oil`; each round and the whole are lane-exact with balanced positions; greedy blocks as stated. 5 is optimal: 2 + ⌈(9 + 35)/17⌉ = 5. Now `3way/v36_oil_x2`. |
| **Qualifying 3×4 at 11 blocks, optimal on all ten fields** | Confirmed. Score (1, 4, 1, 132, 0, 2, 66, −2, 1, 1), which equals the lower bounds. The min-meet bound (−2) follows because min 3 would force every couple to meet exactly 3 times, i.e. a GBTD(4,3). |
| **Hybrids 27 (0/1/8, 9 weeks) and 39 (0/1/12, 13 weeks)** | Confirmed: valid, fair, lane-exact, positions balanced within each format. Shortest possible, since ⌈(v−1)/3⌉ weeks are needed. These are the 28- and 40-bowler one-meeting rounds with one bowler removed, like the library's vacancy files. |
| **No reordering of the main 4-way 20, 24, 36 files reaches spread 2** | Confirmed by the direct z3 model (unsat for all three; sat for the oil-file controls). |
| **36 in fours, main first: the 4-pattern round's 8-week class can't follow round 1's last block** | Confirmed, in a stronger form. The couples that class leaves unused form exactly 4 disjoint K9s ("layers") plus 9 disjoint K4s ("columns"). So a tail foursome must be a layer-foursome or a whole column. Each tail week uses x columns with 9 − x divisible by 4. Columns can't repeat across the 3 clash-free tail weeks, so the pattern is (1,1,1) or (1,1,5). Two one-column weeks can never be couple-disjoint inside a layer (brute force over the 9-point layer). So no 3 clash-free weeks fit, whatever the tail. |
| 15-bowler qualifying, 5×3 at 6 blocks: any one-meeting draw has no symmetry | **Confirmed** by two independent programs (`check/sym15/sym.c` and `check/sym15/check.py`, sharing no code, written without reading Astra's). Both list the 19 prime-order types (11 + 5 + 3) and search every one to the end with no solution. Controls: with meetings capped at 2 instead of 1, both find symmetric draws for several types, and with no symmetry the C search finds one in 303 nodes. Details in `check/sym15/RESULT.md`. |
