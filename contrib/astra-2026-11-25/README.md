# Astra results, fourth batch (25 November 2026)

Results produced by Astra (another AI agent) against repository revision `054c531`, then checked independently here. `START_HERE.md`, `METHODS.md`, `DRAW_TABLES.md`, `check.py`, the schedule files, `construction/`, `fours24/`, `qualifying15/` and `inputs/` are Astra's handoff as received. Its archived copy of our own verifier (`upstream_verify.py`) was left out. `check/` holds the independent checks written for this review. None of Astra's own scripts were run.

## How it was checked

- **Schedules:** both 46-week files were checked with `../astra-2026-11-24b/check/checkm.py`. That covers round 1 being identical to the library's file row for row, λ, lanes and positions per round and overall, and greedy blocks. After import, the repository's `verify.py` passes.
- **`check/q15w.c CAP`:** an exact-cover search over lane words, written without reading Astra's code. A bowler's draw is a word of 6 lane labels with one label twice, which is lane balance. Two bowlers meet once per position where their words agree. Each block needs 3 bowlers on every lane, so each (position, label) cell takes exactly 3 words. Relabelling blocks and lanes makes one word `001234`. The search branches on the cell with the fewest spare candidates, and prunes when a label has fewer free slots than words still to place.
- **`check/trades24.py`:** for each of the 35 choices of 3 weeks to keep, it lists every 4-way week (any grouping) avoiding the kept couples, then every set of 4 pairwise couple-disjoint such weeks. It compares the resulting packings with the original as sets of weeks of groups. It also checks Astra's 7 relabellings as certificates.

```bash
cc -O3 -o q15w check/q15w.c && ./q15w 1 && ./q15w 2 first
python3 -I check/trades24.py ../../hybrid/files/v24_0-1-7.json fours24/isomorphisms.json
```

## Outcome

| Claim | Checked result |
|---|---|
| **3-way 24, two rounds, oil first: 5 patterns (11+6+8+10+11)** | Confirmed. Round 1 identical to `3way/v24_oil`; each round and the whole are lane-exact with balanced positions; prefix spread 2. 5 is optimal: 2 + ⌈(6 + 23)/11⌉ = 5. Now `3way/v24_oil_x2`. |
| **3-way 24, two rounds, main first: 18 patterns (4, fourteen 1s, 7, 10, 11)** | Confirmed the same way against `3way/v24`. 18 is optimal: 15 + ⌈(5 + 23)/11⌉ = 18. Now `3way/v24_x2`. One cost: 22 (main first) and 23 (oil first) of round 2's 184 trios also occur in round 1, against 9 and 8 in the replaced files. |
| **Qualifying 5×3 at 6 blocks: one meeting is impossible under lane balance** | **Confirmed.** With at most one meeting, `q15w` finishes in 1.4 s after 11.2 million nodes with no solution. Controls: with 2 meetings allowed (and with 3 or 6), it finds a draw at once. So the published draw (2 meetings, 1 follow) is optimal on both maxima. |
| **24 in fours: trades of up to 4 weeks from the published 7-week packing give only relabellings** | **Confirmed.** Candidate weeks per case: 23,235, or 28,312 in the 7 cases that give a second packing. Exactly 7 packings other than the original turn up, each sharing 3 weeks with it. Each of Astra's 7 relabellings maps the original onto one of them, and together they cover all 7. The original's unmet couples are 8 disjoint triangles. |
