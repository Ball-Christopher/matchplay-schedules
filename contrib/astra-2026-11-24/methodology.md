# Matchplay schedule results and methodology

24 November 2026. Repository revision `e5afce74958754eace59262e1d530d4fb41052ab`. Tables in the companion files give the actual weeks. The oil and main versions of a first round can have very different optimal continuations.

## 1. Four oil patterns for 24 bowlers in fours

**Four patterns suffice, and four is optimal.** The witness has 23 distinct weeks in blocks of 6, 6, 6 and 5. A bowler can meet at most 23 opponents, three per clash-free week, so three patterns hold at most 21 weeks.

Label players by the 24 permutations of four objects. Left multiplication by the symmetric group acts on the players. It permutes the three six-week patterns as it permutes the three partitions of four objects into two pairs. The stabilizer of one such partition has order eight. The five-week pattern is invariant as a set. For each possible week stabilizer, generate candidate orbits of foursomes, discard any that repeat a couple on one pattern, and use exact-cover constraints to put each player into one group in each week. Constrain each orbit of unordered pairs to multiplicity three across all four patterns. The solution has week orbits of sizes 12, 3, 3, 4 and 1. Expanding the orbits gives a certificate that can be checked without a solver.

The four-pattern witness has prefix spread two. The assigned lanes are unequal. A different schedule in the same file achieves exact lanes and spread two.

## 2. Minimum repeats with 12 bowlers in fours

**The minima are 40 with three patterns and 27 with four.** Morales and Velarde classified the underlying designs. Their five representatives reduce the problem to a small exhaustive calculation. Repeated foursomes cannot evade the classification. If four players shared a group twice, their six pairs would have just six remaining meetings available. In each of the other nine weeks at least two of those four must share one of the three lanes, requiring at least nine meetings.

| Published design | Resolutions found | Minimum, three patterns | Minimum, four patterns |
|---|---:|---:|---:|
| 1 | 1 | 40 | 27 |
| 2 | 1 | 41 | 27 |
| 3 | 1 | 43 | 28 |
| 4 | 1 | 41 | 27 |
| 5 | 1 | 42 | 28 |

For each design, enumerate triples of disjoint foursomes, then all exact covers of the 33 foursomes by 11 such weeks. A subset of weeks S costs 18 times its size minus the number of distinct pairs it covers. Minimize the sum over partitions into three or four nonempty subsets. Every partition becomes a consecutive split by scheduling each subset together. Both published schedules in the companion file attain their stated minima.

[Morales and Velarde, Journal of Combinatorial Designs (2001), Table II and Theorem 4.1](https://doi.org/10.1002/jcd.1019)

## 3. Lane-exact fours with one meeting per couple

**40 exists.** Use the 40 points of projective three-space over the field of three elements. The lines have four points and each pair determines a unique line. Represent a point by a nonzero five-coordinate vector whose entries sum to zero, identifying it with its negative. Cyclic coordinate shift has order five. Enumerate spreads (sets of ten lines partitioning the points). Select two five-spread orbits and three fixed spreads that together partition all 130 lines. Let the same symmetry cycle the first five and the last five lanes separately. A search over representative lane assignments produced the displayed 13 weeks.

**The construction also gives infinite families.** In particular, 28 and 40 can each be multiplied by 16 repeatedly. The first two enlargements, 448 and 640, were expanded and every pair and lane count checked. Here is the construction. Suppose the base has v=4n players, n at least seven. Inflate each player to a fibre of 16. Replace each base week by 16 weeks indexed by a in GF(16) and each lane by 16 sublanes indexed by b. For a base foursome, index its four players by distinct nonzero field elements c. In week a on sublane b use the copy b+ca of each player. Distinct fibres meet exactly once when their original players met, and every copy visits every sublane once per original lane visit.

Five further weeks cover pairs within each fibre using the five directions of the affine plane of order four. Each original player has (2n+1)/3 lanes visited once. Each lane has four times that many single-visit players. Split each lane into four equal-degree clones in this incidence graph. The resulting regular bipartite graph decomposes into perfect matchings. Use five different matchings, one per additional week. The four fibres assigned to a lane each receive four of its sublanes that week. Since a fibre uses a particular original lane at most once in these five weeks, each copy finishes with one or two appearances on every sublane. The complete spectrum of admissible roster sizes remains open.

## 4. Short-season spread

For 20 in fours the existing oil round has exact lanes and worst prefix spread two. Six clash-free weeks are impossible, so two is optimal. For 24 in fours a search intermediate, `ord24_1203.json`, already gives exact lanes and spread two. Reassigning playing positions inside each foursome balances positions without affecting opponents or lanes. That schedule has 21 distinct weekly partitions. The four-pattern solution has all 23 distinct. The best possible spread for 24 lies between one and two.

## 5. Two rounds, first round held fixed

| Group size | Roster | Main first round, lower–upper | Oil first round, lower–upper |
|---:|---:|---:|---:|
| 3 | 18 | 6–6 | 5–5 |
| 3 | 24 | 18–19 | 5–6 |
| 4 | 20 | 19–19 | 8–8 |
| 4 | 24 | 15–20 | 11–16 |

Each upper bound has a witness in the two-round file. The first round is identical to the chosen repository file down to lane and position. Each complete two-round witness and both individual rounds have exact lanes and balanced positions. For 12 in trios, six blocks were already known. For 12 in fours, each block can contain only one week by the pigeonhole principle, so 22 blocks are required over two rounds. The one-round full-roster lane obstruction still applies.

To obtain the lower bounds, greedily take the longest clash-free prefix repeatedly. Moving the first cut later to the greedy cut preserves feasibility by shortening later blocks, so this rule is optimal for a fixed order. If round one takes g blocks with final length t, the first g−1 cuts persist under any continuation. At least g−1+ceil((t+r)/L) blocks are required, where L is the maximum clash-free run and r is the second-round length.

For 18 in trios with the oil first round, keep its 8+5+4 split. Extend the final four weeks by two new weeks. Those two weeks and the following seven cover every pair, with a perfect matching of pairs covered twice. Relabel an eight-week nearly Kirkman triple system to miss exactly that matching. This gives 8+5+6+7+8. An order-three symmetry made the covering and the combined lane constraints small enough to solve. Other constructions use a relabelled second round, assigning its low-usage lanes and positions to complement the first round. All block counts were recomputed from the actual concatenated weeks.

## 6. Rotating the vacancy

Designate any player of a lane-exact full-roster design as the vacancy. The vacancy then visits each lane exactly as evenly as that player did. Conversely, fill the vacancy with a dummy. For the schedules in this problem, a real player who meets each other real player λ times must also meet the dummy λ times, by counting their total opponent slots. Thus the vacancy requirement together with exact real-player lanes is equivalent to full-roster lane exactness. This settles the listed cases. It is impossible at full-roster sizes 15 in trios and 12 or 16 in fours. The vacancy tables give all the positive sizes considered here, including the new 40-player construction.

[Matchplay schedules, pinned source revision](https://github.com/Ball-Christopher/matchplay-schedules/tree/e5afce74958754eace59262e1d530d4fb41052ab)
