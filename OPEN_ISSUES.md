# Open issues

The work still to do, as a checklist. Each item says what's best so far, what would close it, and where to pick it up. The mathematical background is in [OPEN_PROBLEMS.md](OPEN_PROBLEMS.md), and how things were built is in [METHODS.md](METHODS.md).

Status as of 24 November 2026. Contributions are welcome: open a GitHub issue or pull request, with the weeks in the repository's JSON format so they can be checked (`python3 verify.py`, `python3 hybrid/verify.py`, `python3 qualifying/verify.py`).

## Matchplay library (3-way and 4-way, 11–40 bowlers)

| Issue | Best so far | Closed by | Start from |
|---|---|---|---|
| 4-way 24, short-season spread | Spread 2 (lane-exact) | A spread-1 round, or a proof it can't exist. It needs a 7-week clash-free packing whose unmet couples form six disjoint 4-cycles. | OPEN_PROBLEMS 3; Astra's 6×6-board construction in `contrib/astra-2026-11-24/` |
| 4-way 20, 24 and 36 main rounds peak at spread 3 | Spread 3 | Lane-exact main rounds with spread 2. The oil rounds of 20, 24 and 36 already reach 2. | METHODS 8 and 11 |
| Prefix order searched jointly with lanes | Order tuned after lanes are fixed | A joint search | METHODS 11 |

These are impossible and can't be fixed: exact lanes for 3-way 15, 4-way 12 and 4-way 16, and a rotating vacancy for 14 in trios and for 11 or 15 in fours.

## Two rounds in oil patterns (round 1 fixed)

| Size | Oil round first | Main round first | Start from |
|---|---|---|---|
| 3-way 24 | 6 (bound 5) | 19 (bound 18) | Astra tried recolourings and fixed-tail embeddings; see `contrib/astra-2026-11-24b/search_notes_under_40.md` |
| 3-way 36 | 6 (bound 5) | 24, optimal | **Partial:** the bridge in `contrib/astra-2026-11-24b/resume36/` extends round 1's tail to 12 weeks. What's left is lanes, positions and the transversal weeks (its `START_HERE.md`, steps 2–5). |
| 4-way 36 | 8 with the new 4-pattern round (bound 7) | 30 (bound 29) | Needs a different round 2. Astra's 4-pattern round has a unique 4-colouring, 8+9+9+9. |

All other sizes are optimal (OPEN_PROBLEMS 4).

## Lane-exact one-meeting fours (λ = 1)

- **88 bowlers:** open. It is the only open size below 160. Astra's Z_21 × 4 + 4 search found nothing. Everything else from 28 to 148 is solved (OPEN_PROBLEMS 2).
- **Positions at 448 and 640:** these witnesses have exact lanes but unbalanced positions. A de Werra recolouring (METHODS 7) should fix them.

## Hybrid seasons (format changes so every couple meets once)

| Issue | Status | Start from |
|---|---|---|
| **37 bowlers** | No schedule within 16 weeks. 0/6/8 (14 weeks), 0/12/4 (16) and 6/3/8 (17) were not found. Many symmetry groups are ruled out. | `hybrid/tools/mixed/` (`gsat.py`, `ggsat.py`, `sanneal.c`); logs in `logs/g/` |
| 24 bowlers, 2×2-way + 7×4-way | Not found; also open in the published literature (URD({2,4}; 24) with r2 = 2) | `hybrid/tools/uniform/symsat.py`, `labeled_sat.py` |
| 24 bowlers, 1×2-way + 2×3-way + 6×4-way | Not found | as above |
| 25 in 10 weeks (0/6/4); 31 in 11 or 13 (0/3/8, 0/9/4) | Not found; Z_6 templates gave no answer in an hour | `hybrid/tools/mixed/gtemplates.py` |
| Better lanes | 24 in 8 weeks is 12 off (bound 1); 36 in 12 weeks is 19 off (bound 1); 36 in 14 weeks is 7 off; other 36 files 1–11 off | `hybrid/tools/uniform/lanes.c` |
| Mixed sizes not found | 21 0/4/4, 26 1/0/8 and 7/0/6, 27 0/1/8, 33 4/2/8, 34 3/3/8 and 3/0/10, 38 1/3/10; 39 not attempted | `hybrid/tools/mixed/` |
| Citations | Some entries in `hybrid/LITERATURE.md` came from search snippets and are marked as such; they need confirming against the papers | `hybrid/LITERATURE.md` |

Full results and proofs: [hybrid/README.md](hybrid/README.md).

## Qualifying movements

| Issue | Best so far | Start from |
|---|---|---|
| 5×3 at 6 blocks | 2 meetings, 1 follow; 1 meeting not ruled out (the Kirkman argument doesn't cover packings outside a KTS(15)) | `contrib/astra-2026-11-24b/search_notes_under_40.md` |
| 3×4 at 11 blocks, follows | 4 meetings (optimal), 2 follows (bound 1) | `qualifying/anneal.c` |
| Other entries marked `?` | Listed under "Open" in [qualifying/README.md](qualifying/README.md), mostly B = 7–12 with 1 meeting not ruled out | `qualifying/exact.py`, `qualifying/anneal.c` |

## Housekeeping

- `contrib/astra-2026-11-24b/two_rounds/4w36_oil.json` extends the **old** 11-pattern oil round, which the library has since replaced. It is kept as received.
- The 2019 North City Singles archive file (`hybrid/files/v24_archive2019.json`) keeps its original, unbalanced lanes for comparison. The balanced version is `v24_0-10-1`.
