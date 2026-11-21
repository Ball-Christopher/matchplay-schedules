#!/usr/bin/env python3
"""Vacancy variants v{N}_vacant.json/.toml: the design point v is the vacant slot
(its group plays three-handed). Lane-pair balance is required for real players only;
the vacancy takes part in the position colouring as if it were a player.
Usage: python3 vacant.py [12 16 24 28]"""
import json, sys
import lanes as L, positions as P
from build import record, write_toml

def cyclic_fixed_lanes(weeks):
    # rotational() emits block j of the base week at index j in every week:
    # block j on lane pair j => each finite point is on lane j |B_j \ {inf}| times.
    return [list(map(list, wk)) for wk in weeks]

def make(v):
    F = json.load(open("final_inputs.json"))
    main = F.get(str(v), {}).get("weeks")
    if v == 12:
        W, st = L.balance_lanes(main, 120, ignore=(v,)); assert st == "sat"
        method = ("Same design and week order as v12.json (z3 SAT, prefix spread 2); lane pairs re-solved by z3 "
                  "with bowler 12 as the vacancy, exact for the 11 real players. Used instead of the 1-rotational "
                  "Z_11 design (also exact with block j on lane j) because its prefix spread is better.")
    elif v == 16:
        W, st = L.balance_lanes_opt(main, 200, excess_first=True, ignore=(v,))
        method = ("AG(2,4), lanes by z3 optimisation ignoring the vacancy (16). Exact is impossible: a lane pair holds "
                  "one line per parallel class (5 pairwise-meeting lines); covering all 15 real bowlers needs all 5 "
                  "lines through one point, and two such pencils share a line. The order-5 1-rotational form of AG(2,4) "
                  "(GF(16), x->g^3 x, 0 fixed) has base lines with orbit compositions (1,1,1),(0,2,2),(2,0,2),(2,2,0), "
                  "so fixing block j on lane j is not balanced either.")
    elif v == 24:
        cyc = json.load(open("sweep24_best.json"))["weeks"]
        W = cyclic_fixed_lanes(cyc)
        method = ("1-rotational Z_23 u {inf} design (base week developed mod 23, weeks ordered by beam search for "
                  "prefix spread); base block j kept on lane pair j, so every real bowler is exactly 4,4,4,4,4,3; "
                  "inf = 24 = vacancy, its three-handed group always on lane pair " )
    elif v == 28:
        W, st = L.balance_lanes(main, 120, ignore=(v,)); assert st == "sat"
        method = ("Same as v28.json: 1-rotational over (Z_9 x 3) u {inf} with inf = 28 as the vacancy; lane pairs exact "
                  "for all players already. Note: no design developed over Z_27 can have only 9 weeks (that gives 27), "
                  "so the 1-rotational form for lambda=1 uses Z_9 acting on 3 point classes.")
    W = P.assign_positions(W)
    if v == 24:
        lane_inf = {next(l for l, G in enumerate(wk) if v in G) for wk in W}
        method += "/".join(str(l + 1) for l in sorted(lane_inf)) + "."
    d = record(v, {12: 3, 16: 1, 24: 3, 28: 1}[v], W, method, "Vacancy = player %d; its group of 4 contains 3 real bowlers." % v, vacant=v)
    json.dump(d, open(f"v{v}_vacant.json", "w"), indent=1)
    write_toml(f"v{v}_vacant.toml", W, f"{v-1} bowlers + vacancy {v} (three-handed group), 4-way, {len(W)} weeks. "
               "Chunks of 4 = lane pairs; order = [L1st, R1st, L2nd, R2nd].")
    print(f"v{v}_vacant exact(real)={d['lane_balance_exact']} off={d['lane_off']} prefix={d['prefix_spread']}")

if __name__ == "__main__":
    for v in (sys.argv[1:] or ["12", "16", "24", "28"]):
        make(int(v))
