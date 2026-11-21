#!/usr/bin/env python3
"""Step 2: choose design + week order + lane-pair order per roster -> final_inputs.json."""
import json, sys
import lanes as L
D = json.load(open("designs_raw.json"))
F = json.load(open("final_inputs.json")) if len(sys.argv) > 1 and sys.argv[1] == "--keep" else {}
args = [a for a in sys.argv[1:] if a != "--keep"]
def want(v): return not args or v in args
if want("16"):
    F["16"] = {"lambda": 1, "weeks": json.load(open("lanes16_out.json")),
               "method": D["16"]["method"] + " Lane pairs: z3 optimisation (lanes16.py).",
               "notes": "Exact lane-pair balance is impossible for AG(2,4) (unique resolvable 2-(16,4,1)): "
                        "a lane pair gets one line from each parallel class and only a pencil covers all 16. "
                        "Chosen: max 3 on any lane pair and the minimum 16 (bowler, lane-pair) zeros; 12 bowlers off. "
                        "Over 4 cycles with lane shifts 0,1,2,3 every bowler is exactly 5 per lane pair. "
                        "lambda=1, so any week order has prefix spread 1."}
if want("28"):
    W, st = L.balance_lanes(D["28"]["weeks"], 300); assert st == "sat"
    F["28"] = {"lambda": 1, "weeks": W, "method": D["28"]["method"] + " Lane pairs: z3 PB model, exact.",
               "notes": "base week (0-based; class*9+x, 27=inf): " + json.dumps(D["28"]["base"]) +
                        ". lambda=1, so any week order has prefix spread 1."}
if want("12"):
    src = "sat_v12_22222222220.json"
    W0 = json.load(open(src))["weeks"]
    W, st = L.balance_lanes(W0, 120)
    exact = st == "sat"
    if not exact:
        W, st = L.balance_lanes_opt(W0, 120)
    F["12"] = {"lambda": 3, "weeks": W,
               "method": "z3 SAT model of the whole 11-week resolvable 2-(12,4,3) design with every prefix spread <= 2 (sat_prefix.py); "
                         "lane pairs by z3 PB " + ("(exact)." if exact else "optimisation (exact unsat)."),
               "notes": "Prefix spread 2 at W=2..4 is forced: any two weeks of 3 groups of 4 share a couple (pigeonhole), and z3 proves "
                        "spread 1 infeasible at W=3,4. W=10 is always 1 (complement of the last week). "
                        "Exact lane balance (4,4,3) reported unsat by z3 for this design and for 60 cyclic designs tried."}
if want("24"):
    # design: anneal_prefix.py (seed 3, width-2 windows, seeded from the best cyclic
    # ordering in sweep24_best.json); lanes: lanes.balance_lanes_anneal (lanes_sa_runs.py seed 2)
    W = json.load(open("lsa_ann_2.json"))["weeks"]
    F["24"] = {"lambda": 3, "weeks": W,
               "method": "Started from a 1-rotational Z_23 u {inf} design (base week by annealing, weeks ordered by beam "
                         "search); then simulated annealing over the whole schedule keeping exact lambda=3 and pushing every "
                         "prefix into a width-2 window (anneal_prefix.py). Lane pairs: annealing over within-week orders.",
               "notes": "Prefix spread is 2 except W=11,12 (3; 3 couples outside the window). z3 (15 min) and z3 LNS repair "
                        "did not close it. Exact lane balance not found (z3 PB unknown after 200 s, glpsol worse); best has "
                        "11 (bowler, lane-pair) cells at 5 instead of <= 4."}
json.dump(F, open("final_inputs.json", "w"))
print("inputs:", sorted(F))
