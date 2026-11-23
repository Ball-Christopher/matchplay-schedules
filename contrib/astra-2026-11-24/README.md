# Astra results, 24 November 2026

Results produced by Astra (another AI agent) against repository revision `e5afce7`, then checked independently here. The `.md` files are Astra's write-up as received. `results/` holds Astra's JSON certificates. `check/` holds the independent checkers written for this review; none of Astra's own scripts were run.

## How it was checked

- `check/check.py FILE.md` parses every table or week list in a write-up and recomputes from the weeks alone: week validity, pair counts (λ), lane counts, position balance, worst prefix spread, distinct weeks, block lengths and within-block repeats.
- `check/check12.py results/designs12.json` checks the five resolvable 2-(12,4,3) designs. It confirms each is valid and simple, counts its resolutions by exhaustive search, and computes the exact minimum number of repeats over all splits into 3 or 4 blocks.
- The first round of each two-round witness was compared with the repository file it claims to extend.

```bash
python3 -I check/check.py one_round.md vacancies.md two_rounds.md further_schedules.md large_schedules.md
python3 -I check/check12.py results/designs12.json
```

## Outcome

Every stated property was reproduced. There were no discrepancies.

| Claim | Checked result |
|---|---|
| 24 in fours, 4 oil patterns (6+6+6+5) | Valid, λ=3, 0 repeats, spread 2; lanes **not** exact (as Astra states). The library's own lane-exact 4-pattern file (6+5+6+6) is better. |
| 12 in fours: minimum repeats 40 (3 blocks), 27 (4 blocks) | Witnesses valid. All five designs reproduce the table exactly (40/41/43/41/42 and 27/27/28/27/28). Each has a unique resolution. Completeness depends on the Morales–Velarde classification (five designs), which Krčadinac's S(2,4,37) paper also cites. |
| Lane-exact one-meeting fours at 112, 160, 448, 640 | All four valid: every couple once, every bowler on every lane pair 1 or 2 times. Positions are balanced at 112 and 160 but not at 448 or 640 (as stated). |
| Vacancy schedules (11, 17, 20, 23, 26 in trios; 19, 23, 27, 39 in fours) | All lane-exact for real bowlers. The empty slot visits every lane pair ⌊r/n⌋ or ⌈r/n⌉ times. |
| Two-round witnesses (8 files) | All lane-exact, positions balanced, block lengths and spreads as stated. Round 1 matches the repository exactly, except 4w24 oil. That one extends the **old** 8-pattern `v24_oil`, which the library has since replaced. |
| 20 and 24 in fours, lane-exact spread 2 | Valid as stated. The 20 file equals the library's `v20_oil`. |
