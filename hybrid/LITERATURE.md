# Literature check: uniform and mixed resolvable schedules with block sizes {2,3,4}

Scope: v = 11..40 players, every pair together exactly once, weekly groups of size 2, 3 or 4, optional lane balance.
Method: web search plus reading Schuster 2013 and Dinitz-Ling-Danziger 2009 in full text. Items marked (snippet) were taken from search summaries only; verify before citing. Items marked (memory) are from my recollection and not checked this session.

## 1. Uniformly resolvable designs (URD): every class has a single block size

Notation: r_k = number of classes of block size k. At each point, sum of (k-1)*r_k = v-1.

**URD({2,3}), Rees 1987 (proved).** Exists with r2, r3 > 0 iff v = 0 (mod 6), r2 = v-1-2*r3, and 1 <= r3 <= v/2 - 1. Exceptions: (v, r3) = (6, 2) and (12, 5).
- (v, r3) = (12, 5) has r2 = 1, so it is NKTS(12), and nonexistence of NKTS(12) is a known classical fact (Kotzig-Rosa; snippet only). So NKTS(v) (r2 = 1) exists for all v = 0 (mod 6) except 6 and 12.
- For v <= 40 this covers v = 12, 18, 24, 30, 36, all r3 in 1..v/2-1, except (12,5).
- Rees, "Uniformly resolvable pairwise balanced designs with blocksizes two and three", J. Combin. Theory Ser. A 45(2) (1987) 207-225.
- Statement as quoted in Schuster 2013, Thm 1.7.

**URD({2,4}), Dinitz-Ling-Danziger 2009 and Schuster (proved except where listed).** Exists with r2, r4 > 0 iff v = 0 (mod 4) and r2 = v-1-3*r4 (r2 >= 1).
- Exceptions: (v, r2) = (8, 1) and (20, 1).
- Open for v <= 40: only (v, r2) = (24, 2), i.e. r4 = 7. The other open cases in the list are all v >= 68.
- Statement as quoted in Schuster 2013, Thm 1.8.
- J.H. Dinitz, A.C.H. Ling, P. Danziger, "Maximum uniformly resolvable designs with block sizes 2 and 4", Discrete Math. 309 (2009) 4716-4721, doi:10.1016/j.disc.2008.05.040.
- The r2 = 1 cases are 4-RGDDs of type 2^(v/2), from Ge-Ling, J. Combin. Des. 13 (2005) 222-237.

**URD({3,4}), Schuster and Ge (proved).** Necessary conditions (Schuster 2013, Thm 1.9): v = 0 (mod 12), r4 odd, r3 = (v-1-3*r4)/2, and r_k > 1 implies v >= k^2. Hence r3 = 1 (mod 3).
- v = 12: r4 = 1 (r3 = 4) exists, since a 3-RGDD of type 4^3 plus its groups gives an RGDD(3,4;12). r4 = 3 (r3 = 1) does NOT exist. Rees-type exceptions are listed only for v = 12.
- v = 24: all admissible (r3, r4) = (10,1), (7,3), (4,5), (1,7) exist.
  - Explicit v = 24 designs are printed in E. Schuster, Discrete Math. 309 (2009) 2452-2465, Examples A.6 (r4 = 3) and A.7 (r4 = 5). The Schuster-Ge online resource (Des. Codes Cryptogr. 57, 2010), Example A.15, gives URD({2,4}; 24) with r2 = 5. All three were transcribed (`tools/uniform/out/`). `v24_5-0-6` uses the A.15 design; `v24_0-7-3` and `v24_0-4-5` use alternative designs found by z3, which gave better lanes (added 24 Nov 2026).
- v = 36: all admissible (r3, r4) = (16,1), (13,3), (10,5), (7,7), (4,9), (1,11) exist (Schuster 2013, Lemmas 3.1 and 3.2, from Theorems 1.10-1.12).
- r3 = 1 needs v >= 24 (Thm 1.11); r4 = 3, 5, 7 exist for all v = 0 (mod 12) except v = 12 (Thm 1.12).
- Overall (Schuster 2013, Thm 3.27): all admissible URD({3,4}; v) with v < 200 exist, except v = 12 with r4 = 3, and possibly v in {84, 108, 120, 132, 156} for a few large r4.
- E. Schuster, "Small uniformly resolvable designs for block sizes 3 and 4", J. Combin. Des. 21 (2013) 481-523, doi:10.1002/jcd.21361.
- E. Schuster and G. Ge, "On uniformly resolvable designs with block sizes 3 and 4", Des. Codes Cryptogr. 57 (2010), doi:10.1007/s10623-009-9348-1.

**URD({2,3,4}) with all three sizes present: nothing found in the literature.**
- Present-day search found no paper on URDs with three block sizes of complete blocks.
- The Lo Faro-Milici-Tripodi paper "Uniformly resolvable decompositions of K_v into paths on two, three and four vertices" (arXiv:1406.4279, 2014) is about paths P2, P3, P4, not triples and quadruples. It is NOT relevant to this problem.
- Necessary condition (my own deduction, not from a paper): all three sizes present forces v = 0 (mod 12), so only v = 12, 24, 36 are in range.
- Easy construction (my own deduction): any URD({3,4}; v) with r4 >= 2 gives URD({2,3,4}; v) by splitting j of its 4-classes into 3j pair classes. Each K4 has three perfect matchings, so r2 = 3j, 1 <= j <= r4-1. This gives all (r2, r3, r4) with r2 = 0 (mod 3), r4 >= 1 at v = 24 and 36.
- Cases with r2 not divisible by 3 would need either the {2,4} or {2,3} results combined, or a computer search. Nothing found.

## 2. Mixed-class resolvable PBDs (classes may contain several block sizes)

- **Class-uniformly resolvable designs (CURDs).** Each class has the same multiset of block sizes. Introduced by Lamken, Rees and Vanstone, "Class-uniformly resolvable pairwise balanced designs with block sizes two and three", Discrete Math. 92 (1991) (memory). Danziger and Stevens, "Class-uniformly resolvable designs" and "Class-uniformly resolvable group divisible designs I, II", Electron. J. Combin. 11(1) (2004) R23, R24, build infinite families for sizes {2,3} and {3,4}. The existence theory is sparse and mostly asymptotic or extremal.
- Dinitz and Ling proved extremal families for sizes {2,3}.
- **Resolvable PBD with block sizes {3,4} or {2,3,4}, mixed classes: found no existence theorem.**
- Non-resolvable background: Colbourn, Rosa and Stinson, "Pairwise balanced designs with block sizes three and four", Canad. J. Math. 43 (1991): necessary conditions sufficient for large v (snippet: v > 96). Not directly relevant, since they are not resolvable.
- **Fairness condition (each player has equal numbers of weeks at each group size): nothing found.** CURDs do not give it. Every class has the same block-size profile, but individual players can still differ in which sizes they sit in.
- **Social golfer with unequal groups.** Miller et al., breakout-room allocation, "Social golfer problem with adjacent group sizes" (Symmetry 13(1):13, 2021; snippet). Group sizes differ by at most one, and the pair condition is "at most once", not "exactly once". It has no exact design theory. Nothing found for exact pair coverage with sizes {2,3,4}.

## 3. Lane or court balance

- **Single block size.** BTD(n) (pairs, n lanes, n*(2n-1) array): exists iff n != 2 (Schellenberg, van Rees, Vanstone, Ars Combin. 3 (1977) 303-317; snippet).
- GBTD(k, m) means a resolvable (km, k, k-1)-BIBD arranged m x (km-1) with each point at most k times per row. GBTD(2, m) exists iff m != 2. GBTD(3, m) exists for all m != 2 (Lamken, Des. Codes Cryptogr. 3 (1993), "Existence results for GBTDs with block size 3"; snippet). GBTD(4, m) exists iff m >= 1, m != 2, 3 (Chee, Kiah et al.; snippet, check authorship).
- Lamken, "Generalized balanced tournament designs", Trans. Amer. Math. Soc. 318 (1990), doi:10.1090/S0002-9947-1990-0978380-6.
- Related: Kirkman squares (doubly resolvable STS), Howell designs, generalized Howell designs, near-GBTDs (Shan, Sci. China 2009, blocks 4 and 5; snippet).
- **Mixed block sizes with lane balance: nothing found.** None of the GBTD, Howell, Kirkman-square or sports-scheduling sources I located handles groups of different sizes. In the OR literature (Rasmussen-Trick survey, Swartz-Tang pickleball papers, a bowling-tournament software paper by Bhandari) venue balance appears only for single-size groups. So the lane-balance requirement with {2,3,4} appears to be an open or at least un-surveyed problem. It is best treated as a computational (SAT/ILP/search) task.

## Summary of what is proved

- {2,3}: exists iff v = 0 (mod 6) with r2 + 2*r3 = v-1, r2 >= 1, except (6,2) and (12,5) in r3.
- {2,4}: v = 0 (mod 4), r2 + 3*r4 = v-1, r2 >= 1; exceptions (8,1) and (20,1); only unresolved case at v <= 40 is v = 24 with r2 = 2.
- {3,4}: v = 12, 24, 36 have all admissible (r3, r4) except 12 with r3 = 1; r4 is always odd.
- {2,3,4} and mixed classes: no existence theorem found; the {3,4} to {2,3,4} splitting trick is available.
- Lane balance with mixed sizes: nothing found.
