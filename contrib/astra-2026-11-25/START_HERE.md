# Matchplay results · 25 November 2026

| Question | Earlier bound | Result |
|---|---|---|
| 24 bowlers, trios, published oil round first | 5–6 patterns | **5**, with consecutive lengths 11, 6, 8, 10, 11 |
| 24 bowlers, trios, published main round first | 18–19 patterns | **18**, with lengths 4, fourteen single weeks, 7, 10, 11 |
| 15 bowlers qualifying, five lane pairs, six blocks of trios | 1–2 meetings | **2 meetings, 1 directed follow**, optimal on both maxima under lane balance |
| 24 bowlers, seven clash-free fours weeks | Eight missing triangles in the published packing | Its entire component under trades of at most four weeks per step is a single isomorphism class. The even-cycle and six-four-cycle questions remain open globally. |

[Week-by-week trios tables](DRAW_TABLES.md) · [Construction and proofs](METHODS.md) · [Repository issue checklist](https://github.com/Ball-Christopher/matchplay-schedules/blob/054c531cc2d5063a7c105dac2c03585ab145ff86/OPEN_ISSUES.md)

## Files for use

- The two JSON/TOML pairs in `3way/` contain complete 46-week draws. The oil-first draw is `v24_oil_x2` and the main-first draw is `v24_x2`.
- The published 23-week inputs are in `inputs/`. The weekly rows in the corresponding first halves are identical, including lane and position.
- `qualifying15/published_draw.json` is the repository's existing six-block witness. The new contribution there is the lower bound on meetings.
- The inputs, independent census and seven explicit player relabellings for the fours result are in `fours24/`. Its week indices in the census refer to the lexicographically sorted seed weeks used by the checker.
- `construction/symmetric_weeks.json` records the representative weeks and both relabellings for the trios construction. The finished draws can be used directly without rebuilding them.

## Verification

From this directory run the following commands with Python 3 and assertions enabled. The qualifying proof also requires GNU C++17. The fours census can take several minutes. No solver packages or internet connection are needed.

```sh
python3 check.py
python3 upstream_verify.py
python3 qualifying15/run.py > qualifying-recount.txt
diff qualifying15/census.txt qualifying-recount.txt
python3 fours24/verify.py > fours-recount.txt
diff fours24/census.txt fours-recount.txt
```

Passing a repository checkout path to `check.py` additionally compares both first halves directly to its published files. The archived upstream verifier checks the trios JSON and TOML independently. It reports worst prefix spread two for both complete seasons.

## Where to resume

For the 24-bowler fours hybrid, begin from a different seven-week packing or change at least five weeks in one step from the published packing, allowing for player and week relabelling. A leave consisting entirely of even cycles yields two doubles weeks by alternating edges. Six four-cycles give the specific packing required by the spread-one construction. Lane assignment is a further condition.

The remaining fixed-round two-round intervals in the issue list are 36 in fours, 7–8 with the current oil first round and 29–30 with the main first round. The 14–15 interval in the older handoff applies to the superseded eleven-pattern oil first round.
