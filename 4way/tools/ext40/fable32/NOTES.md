# 4-way 32 (exact lanes, 4 oil blocks) and 36 (oil: no progress, one impossibility proof) — 24 Nov 2026

`python3 verify.py` prints ALL OK.

| File | Before | Now |
|---|---|---|
| 4way/v32 | 13 bowlers off on lanes, worst prefix 3 | **lanes exact**, worst prefix **2** |
| 4way/v32_oil | 13 blocks, 17 bowlers off | **4 blocks (8,7,8,8), 0 repeats, lanes exact**, worst prefix 2 (lower bound 4 reached) |
| 4way/v36_oil | 11 blocks, exact | unchanged (4-block template proven impossible, other routes not solved) |

**Follow-up needed outside this folder's remit:** `4way/v32_x2` still has the *old* v32 as round 1. A regenerated
candidate from the new v32 (exact, 0 repeated groups, worst prefix 2) is in `cand_x2/`; it was made with
`ext40/finish.finish_x2(32)` pointed at that folder. README/METHODS tables and `docs/` also need rebuilding.
Old files are kept here as `old_v32*.json/.toml`, `old_v36_oil.*`.

## Task A + B for 32: one design does both

**Why Z_8 (and Z_4 tracks) cannot work.** Let g be an involution of the symmetry group acting without fixed bowlers.
The pair {x, gx} is met 3 times; g permutes those (week, group) incidences, so one is fixed: a g-invariant group in a
g-invariant week, hence on a lane pair fixed by g. So *every fixed-point-free involution must fix a lane pair*. Z_8
rotating 8 lane pairs, or Z_4 rotating two tracks of 4, both violate this (the 16-cell floor seen before is this
obstruction showing up in the lanes). Groups of odd order have no such problem.

**Construction.** Points Z_7 × {0,1,2,3} (id 7c+i) plus 4 fixed bowlers ∞0..∞3 (ids 28..31). i → i+1 moves lane pairs
1–7 up one and fixes lane pair 8.
- 31 weeks = 4 base weeks × 7 translates + 3 invariant weeks. An invariant week is {∞0,∞1,∞2,∞3} on lane pair 8 plus one
  transversal group (one bowler per class) developed mod 7.
- Pair-orbit ("difference type") count: 12 pure + 42 mixed + 16 ∞-class = 70 types, each to be covered 3 times;
  4 × 48 + 3 × 6 = 210. A base week must put the four ∞ in four different groups.
- Lanes: in each base week one group of four class bowlers sits on lane pair 8 for all 7 translates and the other 7 groups
  get a bijection to Z_7. Fixed bowlers: lane pair 8 three times (invariant weeks), each rotating lane pair 4 times,
  automatically. Class bowlers: lane pair 8 four times iff every class appears 4 times over the four lane-8 groups; rotating
  lanes depend only on (lane − i) per class, 27 visits over 7 residues, cap 4. `lanes.py` (DFS) solves it instantly.
- **Oil blocks.** The 7 translates of a base week are clash-free iff the base week uses no type twice. An invariant week can
  join a base block iff the base week avoids its 6 mixed types. Invariant weeks pairwise clash (the ∞ group), so the
  template is 8+8+8+7: three base orbits + one invariant week each, and one base orbit alone.
- **Symmetry that makes the search small.** α: (c,i) → (π(c), 2i), π = (0)(1 2 3), ∞j → ∞π(j) (order 3, normalises Z_7;
  full group Z_7 ⋊ Z_3 of order 21). Weeks: W, αW, α²W, an α-invariant W0, and T, αT, α²T. Blocks: [αᵏW orbit + αᵏT]
  for k = 0,1,2 and [W0 orbit].
  - W0: sampled at random (two α-fixed groups {(0,0)} ∪ 3-cycle, {∞0} ∪ 3-cycle, two α-orbits of 3 groups), kept if its 48
    types are distinct.
  - W: every α-orbit of types needs an exact number of pairs from W (3 − invariant − W0 coverage, divided by 3/|orbit|),
    each type at most once, T's types forbidden. Exact backtracking over groups (`dfs.c`): 2 of the first 6 random
    (W0, T) samples gave a solution within 20M nodes (0.2 s and 4 s).
  - An order-4 class rotation φ (W, φW, φ²W, φ³W) solves the plain design in < 1 s by annealing (`sa.c`, used for the first
    exact-lane v32, `d32a_1.json`) but **cannot** give 4 blocks: 3 invariant weeks under an order-4 map force a φ-fixed
    one, (0,0,0,0), whose types every base week would have to both avoid and cover (enumerated: 0 feasible sets).
  - Annealing without ties, or with an order-2 tie, stalled at cost 6–24 for the oil version.
- **Files.** `d32o_2.json` (used for both v32 and v32_oil; `sol21_1_3.json` is the raw W0/T/W), `d32o_1.json` a second
  design. v32 = free week order (run32.py), v32_oil = blocks kept (finish_oil.py). Both have worst prefix spread 2:
  each 8-week block is nearly a λ = 1 packing.

## 36 oil: what is now known

- **The suggested template (3 base orbits of 9 + the 8 invariant weeks as block 4) is impossible.** With Z_9 × 4 every
  Z_9-invariant week is a transversal week (0,a,b,c). Eight pairwise clash-free ones cover 8 of the 9 differences on each
  class pair; summing differences shows the missing ones form a ninth, so they would be a (9,4;1) difference matrix over
  Z_9, i.e. two orthogonal orthomorphisms of Z_9. There are none: `dm9.py` checks all 225 normalised orthomorphisms
  (exhaustive, < 1 s). This is why the earlier annealing stopped at 5 repeats.
- Ways round it that were tried (all with base weeks W, αW, α²W, α: (c,i) → (π(c), μi + s_c), α³ ∈ Z_9, so one week is
  searched; `f36c.py`, `f36d.py`):
  - Block 4 = 8 base blocks, α-closed, 48 distinct types, where three blocks may form a week fixed by i → i+3 (orbit
    V, V+1, V+2): **no such α-closed set exists** for π = (0)(1 2 3) or id, μ ∈ {1,4,7}, all shift classes (exhaustive
    enumeration; a mod-3 count explains most cases). Without symmetry such sets are common (1 triple + 5 transversals:
    26 of 30 random triples extend, `exF.py`).
  - Invariant weeks spread over the base blocks, 11+11+11+2 (mode 1) and 10+10+10+5 (mode 2): count-feasible configurations
    exist; 456 of them × 10M DFS nodes found nothing; annealing floor 18–30.
  - Five blocks 9+9+9+4+4 (mode 3): annealing floor 18, 8 DFS runs of 30M nodes found nothing.
  - No tie, block 4 = 1 triple + 5 transversals (`f36u.py`): 12 runs × 2 × 150M annealing steps, best cost 18.
  - Z_7 with 8 fixed bowlers: impossible for 4 blocks (two invariant weeks always share a fixed-bowler couple, so 7
    invariant weeks need 7 blocks).
- Not tried: an involution tie (W, βW with β: i → −i, a β-invariant third base week, as W0 for 32); a SAT/CP solver on
  the single-week problem (none installed; nothing was downloaded); non-Z_9 groups.

## Code
- `gen.py`: pair types (orbits under i → i+1) for Z_m × 4 + fixed points; `spec` writes annealer input, `dfs_spec` the
  exact-search input (per-type capacity, per-α-orbit need).
- `sa.c`: annealer on type counts with tied weeks (week fL+j = φʲ(week fL)) and clash penalty. `sa spec seed iters T0 Tend A [restarts]`.
- `dfs.c`: exact backtracking for one tied week. `dfs spec nodelimit [maxsol] [seed]`. `dfs2.c`: same with a
  most-constrained-point rule (not clearly better).
- `lanes.py`: rotating-lane DFS with an optional fixed lane pair.
- 32: `gen32.py`, `t32a.py` + `mk32a.py` (φ-tied plain design → `d32a_1.json`), `f21.py` (α search), `mk32o.py` (lanes + block order → design JSON),
  `run32.py` (writes v32), `finish_oil.py` + `method32oil.txt` (writes v32_oil), `try32main.py`, `check.py`.
- 36: `dm9.py`, `exF.py`, `f36c.py`, `f36d.py`, `f36u.py`.
- Rebuild: `cc -O2 -o sa sa.c -lm; cc -O2 -o dfs dfs.c; python3 f21.py 1 6 20000000; python3 mk32o.py sol21_1_3.json d32o_2.json;
  python3 run32.py d32o_2.json; python3 finish_oil.py 32 d32o_2.json method32oil.txt 60000 1`.

## Compute
About 2 h wall. 32: minutes in total. 36: ~12 cores for ~25 min of DFS/annealing, no result.
