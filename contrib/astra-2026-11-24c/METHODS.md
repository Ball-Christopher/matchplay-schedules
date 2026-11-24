# Constructions and finite exclusions

## Five oil patterns for 36 bowlers in trios

A clash-free week gives each bowler two new opponents. Hence a single pattern contains at most 17 weeks. The fixed first round has greedy runs of lengths 16, 10 and 9. After its first two runs there are 44 weeks to accommodate, so at least 2 + ceil(44/17) = **5** runs are necessary. Greedy cutting is optimal for a fixed ordering since extending the first run as far as possible can only shorten the remaining suffix.

The second round uses the three 12-player layers and eleven internal weeks in `inputs/mixed36.json`. Within a layer every pair meets twice. The weeks split into clash-free blocks of 3, 4 and 4. The first three join the published nine-week tail without repeating a pair.

**Why the original lane construction failed.** If every player visited eleven distinct internal lanes, each lane would hold eleven player-disjoint triples. Each of the three layers could supply at most four triples to it, hence the contributions would be 4, 4 and 3. Twelve lanes require 24 four-triple fragments. Exhausting the group-disjoint fragments within each layer gives maxima of 8, 5 and 8, totaling 21. Independent permutations of the weeks preserve this obstruction. The program regenerates the fragments directly from the groups. It does not trust the earlier fragment lists.

**How the transversal weeks supply the missing freedom.** Split the twelve lanes into three sets of four. In each internal block, each layer uses one set, rotating the sets between blocks. Split each layer into three four-player groups. Each twelve-week transversal block consists of three four-week rounds. In round t, match group indices i, i+t and i+2t in the three layers, using arithmetic modulo three. Independent relabelling of group indices is allowed between the two copies. Each group meets every group in each other layer once per copy.

Within each matched triple of four-player groups, use the additive group of GF(4). In week t on provisional lane g the three player indices are g+t, g+αt, g+α²t, where α²=α+1. Each pair from different groups meets exactly once over four weeks. Independently relabel the four players of a group in each such round, and permute its four lanes week by week. These operations preserve all required meetings.

The following table records the specific supergroup parameters. For each round the three digits give the set of lanes assigned to i=0,1,2 in that order. Corresponding groups from each layer visit each set of four lanes twice across both copies.

| Copy | Round 0 | Round 1 | Round 2 | Indices in layers 0, 1, 2 (in order 0,1,2) |
|---|---|---|---|---|
| First | 210 | 210 | 021 | 012, 012, 012 |
| Second | 210 | 210 | 102 | 201, 120, 120 |

The actual four-player groups, in index order, are:

| Layer | Group 0 | Group 1 | Group 2 |
|---|---|---|---|
| 0 | 5, 21, 8, 10 | 29, 12, 32, 13 | 26, 4, 16, 30 |
| 1 | 17, 15, 19, 23 | 33, 34, 20, 2 | 22, 6, 7, 18 |
| 2 | 35, 3, 9, 25 | 11, 1, 28, 24 | 31, 14, 27, 36 |

For each four-player group its two transversal visits to a set supply exactly eight player-visits to each of the four lanes in aggregate. In a four-week internal block each group of four therefore needs exactly four aggregate internal visits per lane. We enumerated the four-group lane assignments satisfying that constraint, allowing at most four in the short block. Annealing independently inside each set chose internal assignments, player labellings and weekly permutations until each player's total was two or three on each lane. A global lane permutation separated the two rounds' short lanes. Successive integral bipartite flows then filled positions, giving each player a different short position in each round.

Each 16-week block comprises four internal and twelve transversal weeks. Internal and cross-layer opponent pairs are disjoint. Thus the second round has runs 3, 16 and 16. Over both rounds, each of the 630 couples meets four times, each player visits every lane five or six times and plays each position 23 or 24 times. Within each half these figures are two meetings, two or three lane visits and eleven or twelve appearances per position.

## Eleven qualifying blocks for 12 bowlers

Use an order-three permutation cycling each of four triples of bowlers and cycling the three lane pairs. Search three orbits of three blocks and two invariant blocks. Each quartet supplies a directed four-cycle. Penalise duplicated directed arcs, pairs meeting over four times, and lane totals outside three or four. After finding a solution, rotate the four-cycles to balance individual playing positions. Rotations preserve every directed arc. A binary choice among four rotations for each of the 33 quartets gives two or three appearances per position and five or six starts on each side.

Counting the final rows gives 12 couples meeting twice, 42 meeting three times and 12 meeting four times. All 132 ordered pairs occur once in the actual bowling order 1, 3, 2, 4. Each player follows all eleven others exactly once.

**Optimality in repository score order.** Lane spread is at least one because 11 is not divisible by 3. A meeting cap of three would force all couples to meet three times by counting. With balanced lanes that is the nonexistent GBTD(4,3). A positive number of blocks requires at least one directed follow. These observations establish the two maxima. There are 198 undirected meeting incidences and 66 couples, so at least 132 repeats. Zero repeated directed follows is best possible. With directed maximum one, both directions of every pair are used, fixing the undirected follow maximum at two and its repeat count at 66. Minimum meetings cannot reach three, since mean meetings is exactly three and uniformity is impossible. The remaining side and position spreads are at least one by divisibility. The final score vector is (1, 4, 1, 132, 0, 2, 66, −2, 1, 1).

[Chee, Kiah and Wang, Generalized Balanced Tournament Designs with Block Size Four](https://doi.org/10.37236/2717)

## Shortest hybrid seasons for 27 and 39

Delete player 28 or 40 from the corresponding one-meeting fours round. Each surviving player met the deleted player exactly once, so plays in precisely one trio and otherwise in fours. Every surviving pair retains its unique meeting. Keeping the parent lanes preserves lane exactness. For fours, choose positions by successive bipartite matchings between groups and players, giving each player two appearances per position for 27 and three for 39. Each player has a single trio position, so its counts already differ by at most one. With at most three opponents per week, season length is at least ceil((v−1)/3), giving nine and thirteen respectively. Lane counts seven and ten also attain ceil(v/4).

## Fifteen-player qualifying requires an asymmetric packing

A bowler's six lane visits form a word over five lanes with one symbol repeated twice and the other four once. There are 5 × 6!/2 = 1,800 possible words. A one-meeting draw contains fifteen different words. Two words agree in at most one coordinate, and every week–lane cell occurs three times. These conditions are sufficient as well as necessary, since they reconstruct the weekly triples.

The week and common lane relabellings form S₆ × S₅. Player relabelling introduces no kernel because all words are distinct. By Cauchy's theorem, any nontrivial stabiliser contains an element of prime order 2, 3 or 5. For prime p each component permutation is determined up to conjugacy by its number of p-cycles. This gives eleven, five and three nonidentity types respectively. The relative choices of cycle generators are covered by conjugation separately in the two symmetric groups.

For each type, generate all word orbits, including singletons. Discard internally clashing orbits. Two surviving orbits are compatible if the first word of one agrees at most once with every word of the other, since simultaneous rotation preserves agreement. Enumerate compatible subsets in increasing orbit order, pruning a cell used more than three times or insufficient remaining words. At fifteen words, each week's five cells must all have occupancy three. **None of the nineteen searches finds a draw.** This excludes every nontrivial stabiliser, including involutions that fix some bowlers. It leaves asymmetric packings open. The verifier compiles the enumeration, checks coverage of the conjugacy types, and reproduces the recorded search totals.

## Prefix spread of the published 20-, 24- and 36-player main fours

For each couple record the three weeks in which it meets. A prefix has spread three exactly when one such triple is wholly in the prefix and another wholly outside. For an order with spread at most two, choose as pivot the first week after which all couples have met. No triple finishes strictly before the pivot and no triple lies wholly after it. Conversely, if the other weeks can be coloured before/after with neither colour containing a full triple, putting the pivot between the colours gives spread at most two. Thus it suffices to delete the pivot and its incident triples and test two-colourability of the remaining three-uniform hypergraph. The search tries each pivot, propagates forced colours, and branches both ways on unassigned weeks. All pivots fail for each of the three published files. This excludes every reordering of the existing groups; alternative designs remain possible.

## Fixed main round for 36 in fours

The first round's final three weeks would have to absorb the eight-week class of the known four-pattern second round to improve from 30 to 29. Its other three classes each have nine weeks, and the overall cap is eleven. In the eight-week class the players lie on a four-by-nine grid. Each cross-layer pair has already met except pairs in the same column. Any compatible fixed quartet must consequently lie in a single layer or be a full column. If x full columns occur in one tail week, 9−x players in each layer must partition into fours, so x is 1, 5 or 9. Used columns in different tail weeks must be disjoint because the tail has no repeat pair. Across the three weeks only (1,1,1) or a permutation of (5,1,1) fits. Of the assignments, 108 select disjoint columns. For all 108, the remaining quartets force a connected component too large for a layer or force column-mates into the same layer. This excludes the eight-week class for any relabelling. It does not determine the optimum over all second rounds.

[Repository baseline and current issues](https://github.com/Ball-Christopher/matchplay-schedules/tree/61eecc0860c6c990dbac48daecfdb729c06d204b)
