# Searches and remaining questions

## Four-pattern lane balance

The successful symmetric-group construction achieves four patterns. I tested lane actions for the full group and smaller subgroups, within-week lane permutations, and searches that reoptimized two or three lanes at a time. These did not certify an exact lane assignment to the four-pattern witness by this checkpoint. Failure for a particular lane action leaves unrestricted lane assignments open.

For comparison, the best possible number of patterns **within the one-rotational family over 23 finite points and infinity is eight**. Enumerate undirected circulant connection sets on 23 week indices. Remove sets equivalent under multiplication by a nonzero residue and sets contained in an already accepted colourable superset. For seven colours the maximal masks up to equivalence are 1020, 506 and 762 (bit d denotes circular distance d). The repository base-week DFS finds no design for any of the three masks. For eight colours it finds a design for mask 1982. This restricted-family boundary explains why a different symmetry mattered.

Other attempted constructions included a seven-week packing whose missing pairs form six disjoint four-cycles, and five transversal weeks developed across four equal player fibres. Restricted searches using cyclic, dihedral and small permutation groups failed to furnish the desired packing or the simultaneous lane certificate. Some constraint runs timed out. These runs do not settle the unrestricted cases.

## Spread one at 24 in fours

A necessary condition is unusually specific. The first seven weeks must be clash-free, since the average pair count is below one. At week eight it exceeds one, so every pair must have met. Each player is missing exactly two opponents after week seven. Both must be in their week-eight foursome. Inside each foursome the missing edges therefore form a four-cycle. A seven-week packing leaving six disjoint four-cycles would also suffice for the unrestricted spread-one problem, as follows.

Take a six-by-six board with rows and columns each divided into three pairs. Use every cell outside the three diagonal two-by-two squares. The 24 occupied cells are players. Row foursomes form week A and column foursomes form week B. Within each of the six occupied two-by-two rectangles take the horizontal matching H and vertical matching V. The row edges other than H form six four-cycles, the column edges other than V form six four-cycles, and H together with V forms six four-cycles. Relabel three copies of the proposed seven-week packing to leave those three graphs, respectively, in the order row remainder, H plus V, column remainder. Insert A after the first packing and B after the second. After eight weeks every pair has met once, with H doubled. After fifteen weeks all pairs have met twice except V, which has met once. After week sixteen every pair has met twice, with the column remainder tripled. Within each intervening packing the prefix spread never exceeds one. The lane constraint would need an additional argument.

## Larger one-meeting designs

An order-five symmetry search in affine three-space of order four did not furnish a lane-exact 64-player schedule. A 52-player construction using three permuted layers and one fixed layer produced timeouts. Neither result is a nonexistence proof. In contrast, both of the 16-fold enlargements in the accompanying schedules have been checked directly.

## Two-round bridges

Enumerating recolourings of existing one-round designs and trying player relabellings alone failed for the five-block 18-player oil schedule. A new second-round covering solved that case. For 24 in trios, trying to embed a short colour class of the existing oil design across the round boundary did not furnish five blocks. Constrained searches for a replacement covering also remained inconclusive. For 24 in fours, the missing piece for improved lane-exact two-round results is a continuation meeting the lane totals and the clash-free boundary simultaneously.

## Data and interpretation

Exact optima use a counting proof, a published classification followed by exhaustive enumeration, or matching lower and upper bounds. A verified schedule supplies an upper bound even when a better one might exist. The checks use the weekly roster permutations to count every pair, every lane, every position and all within-pattern repeats. The main and oil versions of a first round were checked separately because their literal week orders differ.
