"""Rebuild vacancy files from the lane-exact main round (OPEN_PROBLEMS problem 5).

Any bowler of a lane-exact full round can be the empty slot: it then visits every
lane pair floor(r/n) or ceil(r/n) times, and the real bowlers keep their exact
lanes, positions and pair counts. The bowler chosen is the one whose removal gives
the smallest worst prefix spread (then smallest total), then renumbered to v."""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from schedlib import groups, stats, write

def rebuild(D, v):
    d = json.load(open(f"{D}/v{v}.json")); k = d["group"]; n = v // k
    assert stats(groups(d["weeks"], k), v, k)["lane_off"] == 0, "main round is not lane-exact"
    W = groups(d["weeks"], k)
    best = None
    for p in range(1, v + 1):
        ps = stats(W, v, k, vacant=p)["prefix_spread"][:-1]
        key = (max(ps), sum(ps), -p)
        if best is None or key < best[0]: best = (key, p)
    p = best[1]
    swap = lambda x: v if x == p else (p if x == v else x)
    W = [[[swap(x) for x in g] for g in wk] for wk in W]
    r = len(W); visits = [sum(v in g for wk in W for g in [wk[l]]) for l in range(n)]
    assert max(visits) - min(visits) <= 1
    method = (f"v{v}.json (lane-exact main round) with one bowler made the empty slot, renumbered to {v}. "
              f"The slot visits each lane pair {r // n} or {-(-r // n)} times; real bowlers keep the main round's "
              "exact lanes, balanced positions and pair counts. Bowler chosen for the smallest worst prefix spread.")
    st = write(D, f"v{v}_vacant", W, v, k, 1, method,
               f"# {v - 1} players, {k} per lane pair (one slot empty each week: player {v}), every couple meets {d['lambda']} time(s);\n"
               "# lane pairs exact; empty slot rotates over the lane pairs; positions balanced.\n", vacant=v)
    print(f"{D}/v{v}_vacant: slot visits {visits}, worst prefix spread {max(st['prefix_spread'][:-1])}, lane_off {st['lane_off']}")

if __name__ == "__main__":
    for spec in sys.argv[1:]:
        D, v = spec.split(":"); rebuild(D, int(v))
