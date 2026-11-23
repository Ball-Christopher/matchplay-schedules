"""Write 4way/v40 and v40_vacant from a Z_5-invariant parallelism of PG(3,3) (pg33_z5.jsonl line IDX)
and its equivariant lane solution (pg33_lanes.txt, from lz5b).  Usage: python3 finish40.py IDX"""
import sys, json, itertools
from pathlib import Path
HERE = Path(__file__).resolve().parent
OUT = HERE.parents[2]
sys.path.insert(0, str(HERE.parents[3] / "tools"))
from positions import assign
from schedlib import write, stats

idx = int(sys.argv[1])
d = json.loads(open(HERE / "pg33_z5.jsonl").read().splitlines()[idx])
lanes = next(list(map(int, l.split()[3:])) for l in open(HERE / "pg33_lanes.txt") if l.startswith(f"{idx} SOL"))
blocks = [b for f in d["fixed"] for b in f] + [b for o in d["orbit"] for b in o]
pid = lambda c, a: c + 8 * (a % 5) + 1                      # player number 1..40 (PG point n = class + 8*residue)
def shifted(b, L, g):                                       # block b on lane L, translated by g
    return (L // 5) * 5 + (L % 5 + g) % 5, [pid(c, a + g) for c, a in blocks[b]]
def week(items):
    wk = [None] * 10
    for L, grp in items: assert wk[L] is None; wk[L] = grp
    return wk
fixed = [week([shifted(b, lanes[b], g) for b in (2 * f, 2 * f + 1) for g in range(5)]) for f in range(3)]
orb = [[week([shifted(b, lanes[b], g) for b in range(6 + 10 * o, 16 + 10 * o)]) for g in range(5)] for o in range(2)]
# week order: interleave (lambda = 1, so every order has prefix spread 1)
W = [orb[0][0], orb[1][0], fixed[0], orb[0][1], orb[1][1], orb[0][2], fixed[1], orb[1][2], orb[0][3], orb[1][3], fixed[2], orb[0][4], orb[1][4]]
W = assign(W, 4)
st = stats(W, 40, 4)
assert st["meet"] == [1] and st["lane_off"] == 0, (st["meet"], st["lane_off"])
pc = "/".join(map(str, sorted(set(tuple(sorted(x, reverse=True)) for x in st["position_counts"].values()))[-1]))
METHOD = ("Lines of PG(3,3) (the 2-(40,4,1) design; points = GF(81)*/GF(3)* = Z_40 via x^4+x+2) resolved into 13 spreads by a "
          "parallelism invariant under the order-5 Singer subgroup n -> n+8: 3 fixed spreads (two line orbits each) + 2 spread orbits of "
          "length 5 (ext40/fable40/pg33.py enumerates all 176). Players = Z_5 x 8 classes, lane pairs = 2 tracks of 5, Z_5 rotates each "
          "track and the weeks together, so lane balance reduces to 8 classes x 10 lane pairs. Exact search (lz5b.c): choose the track of "
          "each base block (every class 5..8 visits per track), then the two tracks are independent small DFSs. 48 of the 176 "
          "parallelisms have an exact assignment (1-3 s each, exhaustive); this is parallelism #%d. Lanes exact: every bowler on every "
          "lane pair 1 or 2 times. Week order: lambda=1, any order has prefix spread 1; positions by positions.assign." % idx)
notes = "design (points [class, residue], player = class + 8*residue + 1): " + json.dumps(d) + "; base-block lanes (5*track+offset): " + json.dumps(lanes)
hdr = ("# 40 players, 4 per lane pair, 13 weeks: every couple meets exactly 1 times;\n"
       f"# every bowler on every lane pair 1 or 2 times (exact); positions {pc}.\n")
write(str(OUT), "v40", W, 40, 4, 1, METHOD, hdr)
j = json.load(open(OUT / "v40.json")); j["notes"] = notes; json.dump(j, open(OUT / "v40.json", "w"), indent=1)
stv = stats(W, 40, 4, vacant=40); assert stv["lane_off"] == 0 and stv["meet"] == [1]
hdrv = ("# 39 bowlers (player 40 = vacant slot), 4-per-pair groups, 13 weeks: every couple meets once;\n"
        "# every real bowler on every lane pair 1 or 2 times (exact). The vacancy moves between lane pairs.\n")
write(str(OUT), "v40_vacant", W, 40, 4, 1, "Same schedule as v40 with player 40 as the vacant slot (v40 is lane-exact for all 40, so the 39 real "
      "bowlers stay exact; that group plays three-handed). " + METHOD, hdrv, vacant=40)
j = json.load(open(OUT / "v40_vacant.json")); j["notes"] = notes; json.dump(j, open(OUT / "v40_vacant.json", "w"), indent=1)
print("v40 / v40_vacant written: lanes off", st["lane_off"], stv["lane_off"], "meet", st["meet"], "prefix", st["prefix_spread"])
