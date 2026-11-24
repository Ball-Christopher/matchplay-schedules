# Symmetric one-meeting draws (15 bowlers, 5 lane pairs, 6 weeks): independent check

Written from the spec alone. I did not read or run Astra's code or its expected output.

## Verdict
**Claim confirmed.** For all 19 conjugacy types of prime-order elements (σ,τ) ∈ S6×S5,
no invariant one-meeting draw exists. Two independent implementations agree.

## Programs
- `sym.c` (cc -O2): bitset exact-cover search. At each node it branches on the (week,lane)
  cell with the fewest candidate orbits, which is exhaustive because some chosen orbit must
  cover that cell. Pruning: cell over 3, cross-orbit clash, orbit too large for the
  remaining slots. Siblings exclude the orbits already tried.
  Usage: `./sym AMAX type [nodelimit] [k]`. type -2 lists the types, -1 is the trivial group,
  and k>0 runs sanity test (a).
- `check.py`: a separate Python implementation with its own orbit code. It backtracks over
  orbits in a fixed order (sorted by the lowest cell each covers), which the spec asked for.
  It prunes when a cell goes over 3, when two words clash, when too few words remain, and
  when a cell below the current orbit's lowest cell is still short of 3.

Representatives: σ = a disjoint p-cycles on weeks (0..p-1)(p..2p-1)…, τ = b disjoint
p-cycles on lanes. Action: (σ,τ)·w puts τ(w[i]) at position σ(i).
Word count is 1800. Type count is 11 + 5 + 3 = **19** (the program asserts this).

## Results, one-meeting (agreement ≤ 1)
"orbits" is all orbits of the 1800 words. "clash" counts orbits with an internal clash,
dropped by both programs. "full" counts orbits that alone put more than 3 words in a cell
(sym.c drops these; check.py keeps them, which is why its usable count is higher for type 17).

| # | p | a | b | orbits | clash | full | usable (C) | C nodes | Py nodes | solution |
|---|---|---|---|-------:|------:|-----:|-----------:|--------:|---------:|----------|
| 0 | 2 | 0 | 1 | 900 | 900 | 0 | 0 | 1 | 1 | no |
| 1 | 2 | 0 | 2 | 900 | 180 | 0 | 720 | 121 | 2,585,821 | no |
| 2 | 2 | 1 | 0 | 960 | 840 | 0 | 120 | 25 | 25 | no |
| 3 | 2 | 1 | 1 | 936 | 792 | 0 | 144 | 31 | 37 | no |
| 4 | 2 | 1 | 2 | 900 | 228 | 0 | 672 | 109 | 656,533 | no |
| 5 | 2 | 2 | 0 | 900 | 900 | 0 | 0 | 1 | 1 | no |
| 6 | 2 | 2 | 1 | 912 | 384 | 0 | 528 | 7,001 | 233,257 | no |
| 7 | 2 | 2 | 2 | 904 | 320 | 0 | 584 | 16,601 | 281,853 | no |
| 8 | 2 | 3 | 0 | 900 | 180 | 0 | 720 | 17,405 | 165,665 | no |
| 9 | 2 | 3 | 1 | 900 | 324 | 0 | 576 | 9,577 | 107,189 | no |
| 10 | 2 | 3 | 2 | 912 | 408 | 0 | 504 | 10,701 | 98,829 | no |
| 11 | 3 | 0 | 1 | 600 | 600 | 0 | 0 | 1 | 1 | no |
| 12 | 3 | 1 | 0 | 600 | 600 | 0 | 0 | 1 | 1 | no |
| 13 | 3 | 1 | 1 | 612 | 312 | 0 | 300 | 628 | 7,099 | no |
| 14 | 3 | 2 | 0 | 600 | 0 | 0 | 600 | 7,441 | 16,837 | no |
| 15 | 3 | 2 | 1 | 600 | 120 | 0 | 480 | 6,904 | 15,091 | no |
| 16 | 5 | 0 | 1 | 360 | 0 | 0 | 360 | 361 | 359 | no |
| 17 | 5 | 1 | 0 | 360 | 240 | 120 | 0 | 1 | 1 | no |
| 18 | 5 | 1 | 1 | 360 | 225 | 0 | 135 | 133 | 170 | no |

Run times: C took under 0.01 s per type (all 19 in 0.04 s wall). Python took 0 to 178 s per
type (about 3 min wall with 6 in parallel).

## Sanity tests
(a) Not vacuous. On the trivial group, sym.c finds sets of k = 4, 6, 8 and 10 words that
pairwise agree in at most 1 place, with every cell ≤ 3, in k+1 nodes each.

(b) Relaxed problem (agreement ≤ 2, cells exactly 3, 15 words):
- Trivial group, sym.c: found in 303 nodes. Every solution was re-checked by separate code.
- sym.c by type: FOUND for types 2, 3, 6, 7, 10, 13, 14, 15, 16, 18. Exhaustive NONE for
  0, 1, 4, 5, 11, 12, 17. Types 8 and 9 hit the 2×10^8-node cap (about 37 s each), so they
  are inconclusive (not needed).
  Example invariant under type 16 (τ a 5-cycle):
  `AABCDE BBCDEA CCDEAB DDEABC EEABCD AACBED BBDCAE CCEDBA DDAECB EEBADC AADEBC BBEACD CCABDE DDBCEA EECDAB`
- check.py by type: FOUND for 13, 14, 16 and 18 as well.

Raw outputs are in `out1_*.txt` (C, ≤1), `out2_all.txt` (C, ≤2), `py1.txt` (Python, ≤1)
and `py2.txt` (Python, ≤2).

## Caveat
Like the method, this assumes the symmetry acts as S6×S5 on the set of words. Relabelling
bowlers is implicit because the draw is a set of words.
