# Matchplay handoff · 24 November 2026

**Scope:** leagues of at most 40 bowlers. This was a one-off search. Monitoring is disabled. Use repository revision [33d41db](https://github.com/Ball-Christopher/matchplay-schedules/tree/33d41db) as the comparison point.

## Verified results

Read [league_results.md](league_results.md) for the complete status table. The archive contains **47 in-scope draws**: two one-round matchplay schedules, twelve two-round schedules and 33 qualifying draws. Seven of the twelve two-round optima are proved. Twenty-four qualifying draws improve a published meeting or follow maximum. The published six-block 15-player case remains open. The attached seven-block impossibility proof does not extend to it.

| Fixed first round | Proved minimum patterns over both rounds |
|---|---:|
| 24 in fours, oil / main | 8 / 16 |
| 30 in trios, oil / main | 5 / 18 |
| 32 in fours, oil / main | 8 / 8 |
| 36 in trios, main | 24 |

The 36-player fours round settles the four-oil-pattern question with 9+9+9+8 and attains prefix meeting spread two. The separate 36-player trios round attains 3+16+16. The latter is a complete **one-round** witness. The fixed oil-first **two-round** result at 36 in trios remains **5–6**.

## Resume first with the 36-player trios oil extension

The file [resume36/mixed36.json](resume36/mixed36.json) contains a candidate second-round skeleton using the actual player IDs of the fixed first round. Three layers of 12 each have eleven internal weeks. Within each layer the weeks are ordered in clash-free blocks of 3, 4 and 4. Combining the three layers’ first three weeks extends the published nine-week tail to twelve clash-free weeks. This bridge is verified. Lane labels, positions and the complete second round for this particular bridge are still pending.

1. Run `python resume36/check_checkpoint.py`. The checkpoint includes the fixed first round, layer partition, group assignments and candidate lane fragments; it needs no scratch paths.
2. Try assigning the eleven internal weeks to twelve lanes so each player visits eleven distinct lanes. A single lane must hold eleven mutually player-disjoint triples, one per week. Each layer supplies at most four, so its three layer contributions must have sizes 4+4+3 in some order. The three `subclasses*.json` files enumerate candidate fragments. Each entry is a week bit mask and a list of zero-based group indices, with index `4 * week + group`. Join fragments with disjoint week masks that cover all eleven weeks, then exact-cover all 132 group instances with twelve such lanes. The first, second and third layers respectively have 27, 12 and 27 four-group fragments. Within-block week permutations can be varied independently by layer if the current alignment fails.
3. Add two sets of twelve transversal weeks across the three layers. Three mutually orthogonal Latin squares of order twelve suffice. Index each square by week and lane, and use its entry as the player in its layer. Each copy gives every player one visit per lane and every cross-layer couple one meeting. The SageMath design database lists Brendan McKay’s squares under `MOLS_12_5`. Attach one set of transversal weeks to each internal four-week block, giving a candidate second round of 3+16+16. Each of these three blocks is clash-free. With the fixed first round this gives intended lengths **16+10+12+16+16**.
4. If the internal-week lane cover fails, permit lane permutations in one transversal week of each copy. The completed one-round witness used this relaxation. The two transversal systems may independently relabel the players within layers, preserving all cross-layer pair totals. For that witness, constraining the two systems to have identical lane assignments made the internal lane assignment much harder.
5. Ensure that every player’s less-frequent lane in round two differs from their less-frequent lane in round one. Try a single global lane permutation first. Then assign playing positions with the analogous short-position constraint. Recount both halves, all 70 weeks, greedy pattern lengths and literal equality of the first 35 rows before changing the five-pattern lower bound into an optimum.

There are four isomorphism types of three clash-free weeks of triples on 12 players in the enumeration used here. Their lists of compatible 12-player subsets in the fixed tail have sizes 345, 493, 28 and 86 in enumeration order. Combining those lists produced the recorded partition with two layers of type 1 and one of type 3. Each admits a completion to eleven internal weeks. The original uniform 3+16+16 construction yielded only 28 compatible subsets for its three-week type, with no triple of disjoint subsets covering all 36. Reusing the uniform witness by relabelling alone misses the mixed-layer candidate.

## Other open work

* **24 in trios.** Oil first remains 5–6 and main first 18–19. Direct three-colourings and fixed-tail embeddings have already been tried.
* **36 in fours.** Published oil first remains 14–15 and main first 29–30. The new four-pattern second round provides both upper bounds. The published oil first round is the eleven-pattern file at the pinned commit.
* **24 in fours, prefix spread.** The best verified value is two. Spread one requires a seven-week packing leaving six disjoint four-cycles. A cyclic search on those components gave no witness.
* **15-player qualifying, five lane pairs and six blocks.** A solution with maximum one meeting must lie outside all 49 one-week deletions of the seven classified Kirkman systems. The partial-packing, symmetry and lane-repair searches are described in [search_notes_under_40.md](search_notes_under_40.md).
* **12-player qualifying, three lane pairs of four, eleven blocks.** The meeting optimum is four. The attainable follow maximum is two, with a lower bound of one.

## Verification and file map

Run from the extracted folder with Python 3 and assertions enabled:

```sh
python verify_results.py
python proofs/check_boundary.py
python proofs/check_kirkman.py
python resume36/check_checkpoint.py
```

Supplying a path to a checkout of 33d41db to `verify_results.py` additionally compares every first-round row to the upstream JSON. See [league_methods.md](league_methods.md) for the constructions and proofs. The three Markdown draw tables are [one-round schedules](36_bowler_schedules.md), [two-round schedules](two_round_schedules_under_40.md) and [qualifying schedules](qualifying_schedules_under_40.md). The original problem list and source methods are under `baseline/`.

The optional `earlier_large_leagues/` appendix preserves the seven earlier one-meeting certificates for 52, 64, 76, 100, 124, 136 and 148 bowlers. Its local verifier checks those files separately. The 88-player search did not produce a verified lane-exact schedule. These sizes are outside the active scope.
