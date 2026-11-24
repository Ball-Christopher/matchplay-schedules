# Astra results, second batch (24 November 2026)

Results produced by Astra (another AI agent) against repository revision `33d41db`, then checked independently here. The `.md` files, `qualifying/`, `two_rounds/`, `proofs/`, `resume36/` and `earlier_large_leagues/` are Astra's handoff as received (its copy of our own baseline files was left out). `check/` holds the independent checkers written for this review. None of Astra's own scripts were run.

## How it was checked

- `check/checkq.py .` scores every qualifying draw with the repository's own `qualifying/model.py` (`evaluate`), and compares it with Astra's claim and with the draw in `qualifying/schemes.json`.
- `check/checkm.py FILE.json ...` recounts couples (λ), lane pairs, positions, prefix spread, distinct weeks and greedy clash-free blocks from the weeks alone. For a two-round file it also checks that round 1 is identical to the repository's one-round file, row for row (lanes and positions included), and that each round and the whole are balanced.
- `check/bounds.py` recomputes the two-round lower bound *g* − 1 + ⌈(*t*+*r*)/*L*⌉ for every fixed first round. For 24 and 32 in fours it also lists the groups that avoid every couple in round 1's last block, and enumerates every week (and pair of weeks) that could extend that block.
- `check/kts.py proofs/k15_reps.json` checks that the seven representatives are valid Kirkman triple systems of order 15. For each, it enumerates every lane (one group per week, every bowler once or twice) and searches for five lanes that cover all 35 groups. `check/kts3.py` is an exact isomorphism test, showing the seven are pairwise non-isomorphic.
- `check/bridge36.py resume36/mixed36.json` checks the partial 36-in-trios checkpoint.

```bash
python3 -I check/checkq.py .
python3 -I check/checkm.py two_rounds/*.json fours36_oil.json trios36_product.json earlier_large_leagues/*.json
python3 -I check/bounds.py
python3 -I check/kts.py proofs/k15_reps.json
python3 -I check/kts3.py proofs/k15_reps.json
python3 -I check/bridge36.py resume36/mixed36.json
```

## Outcome

Every stated property was reproduced. There were no discrepancies.

| Claim | Checked result |
|---|---|
| **Lane-exact one-meeting fours at 52, 64, 76, 100, 124, 136, 148** | All seven valid: every couple once, every bowler on every lane pair 1 or 2 times, positions balanced, prefix spread 1. |
| **36 in fours, four oil patterns (9+9+9+8)** | Valid, λ = 3, all 35 weeks distinct, lanes exact (3 or 4 visits), positions balanced, prefix spread 2. Greedy blocks 9, 9, 9, 8. Four is optimal, since a clash-free run has at most 11 weeks. |
| 36 in trios, 3+16+16 | Valid, λ = 2, lane-exact, positions balanced, spread 2. Same block count as the library's `v36_oil`, so it is an alternative, not an improvement. |
| Two-round witnesses (12 files) | All 12: round 1 identical to the repository file; each round and the whole lane-exact with positions balanced; greedy block counts as stated. |
| Two-round lower bounds | Recomputed for all 12. For 24 in fours with the main round first, the 60 groups that avoid round 1's last block don't contain even one complete week, so the bound is 12 + 4 = 16. For 32 in fours, only 7 groups avoid the last block and a week needs 8, so the cut is forced and the bound is 4 + 4 = 8. |
| 33 qualifying draws | All 33 match Astra's (meet, follow) maxima under our scoring, with lane-pair balance at its minimum. 24 improve the published draw on max meetings or max follows. Some of the new draws have more total repeats than the published ones; they still win, since max follows ranks above repeats. |
| 5×3 at 7 blocks needs 2 meetings | Confirmed. One meeting would be a KTS(15). The seven representatives are valid and pairwise non-isomorphic, so they cover all seven classes. None has any split into 5 balanced lanes. |
| 6×4 at 6 blocks, 6×5 at 4–6 blocks need 2 meetings | Checked by hand. 6×4: 24 permutations of 6 symbols at Hamming distance ≥ 5, but the maximum is 18. 6×5: one meeting plus six constant rows gives an OA(36, 4, 6, 2), meaning two orthogonal Latin squares of order 6, which don't exist. |
| 3×3 at 3 blocks, 3×4 at 7 and 11 blocks | Checked by hand. 3×3: two bowlers share a lane word, so they meet 3 times and must repeat a follow direction. 3×4 at 7: a cap of 2 forces every met couple to meet exactly twice, but 21 opponent slots is odd. 3×4 at 11: a cap of 3 would be a lane-exact resolvable 2-(12,4,3), i.e. a GBTD(4,3), which doesn't exist. |
| 36-in-trios checkpoint (partial) | The three 12-bowler layers each have 11 weeks with every couple twice, in clash-free runs of 3, 4 and 4. With the oil round's 9-week tail, the three bridge weeks give a 12-week clash-free run. Lanes, positions and the rest of round 2 are not done. |
