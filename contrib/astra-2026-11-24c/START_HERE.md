# Matchplay open problems · 24 November 2026

Four verified schedules for leagues of up to 40 bowlers. This supplement uses repository revision **61eecc0**, which has the second batch of results and the updated 36-player fours oil round. The earlier handoff compared against **33d41db**. The 36-player trios oil first round agrees row for row with the downloaded upstream file.

| Open issue | Result | Certificate |
|---|---|---|
| 36 in trios, two rounds, published oil first | **Five patterns, optimal.** The greedy cuts are 16 + 10 + 12 + 16 + 16. | [JSON](3way/v36_oil_x2.json) · [TOML](3way/v36_oil_x2.toml) |
| 12 qualifying, three lane pairs of four, eleven blocks | **Four meetings and one follow, optimal.** All ten repository score fields attain their lexicographic optima. | [Qualifying scheme](qualifying/M3_K4_B11.json) |
| 27 mixed hybrid, one trio and eight fours per bowler | **Nine weeks, shortest possible.** Seven lane pairs. | [Hybrid JSON](hybrid/v27_0-1-8_mixed.json) |
| 39 mixed hybrid, one trio and twelve fours per bowler | **Thirteen weeks, shortest possible.** Ten lane pairs. | [Hybrid JSON](hybrid/v39_0-1-12_mixed.json) |

The two hybrid entries adapt full-roster designs already in the repository. In both files every couple meets once, lanes are exact and positions balance within each format. The qualifying optimum closes the one outstanding follow gap among the previous handoff's 33 qualifying rows.

[Week-by-week draw tables for all four schedules](DRAW_TABLES.md)

## Recheck the results

From the extracted folder, run the following commands with Python 3 and assertions enabled. The first command uses the archived published first round. Optionally append the path to a repository checkout to compare directly with its file.

```sh
python3 check.py
python3 verify.py
python3 proofs/fragments.py
python3 proofs/prefix.py
python3 proofs/grid36.py
python3 proofs/check_symmetry.py
```

Only the last command needs a compiler (GNU C++17). The schedule checks have no external Python dependencies. The root `verify.py` is the repository's matchplay checker. The independent `check.py` also checks the halves separately, cuts the patterns from scratch, recomputes qualifying scores with the upstream evaluator, and runs the upstream hybrid checker. It compares the hybrid groups and lanes to the parent draws after deleting the final roster number. `upstream/` contains the original qualifying evaluator and verifying scripts and the repository licence.

## What remains open

| Case | Remaining question or new restriction |
|---|---|
| 15 qualifying, five lane pairs of three, six blocks | One meeting versus two remains open. **Every one-meeting solution must have trivial symmetry** under a common permutation of lanes and a permutation of weeks. The proof covers all 19 prime-order cycle types, including fixed players. Search unrestricted lane-word sets next. |
| 24 in trios, fixed first round | Oil first remains 5–6. Main first remains 18–19. |
| 36 in fours, fixed first round | **Current four-pattern oil file** remains 7–8. **Old eleven-pattern oil file** remains 14–15. Main remains 29–30. The eight-week transversal class of the handoff's four-pattern design cannot join the published main round's three-week tail, for any player relabelling. |
| 24 in fours, short-season spread one | A seven-week packing leaving six disjoint four-cycles is still needed. |
| 20, 24 and 36 in fours, main files, spread two | Every ordering of each file's existing weeks has a prefix of spread at least three. Improving these main draws requires changing the weekly groups. The existing oil draws already reach spread two. |
| Other hybrid and qualifying items | The remaining hybrid sizes, lane improvements and unlisted qualifying cases retain the status in the repository issue list. |

[Construction and proof details](METHODS.md) · [Repository issue checklist at the comparison revision](https://github.com/Ball-Christopher/matchplay-schedules/blob/61eecc0860c6c990dbac48daecfdb729c06d204b/OPEN_ISSUES.md)
