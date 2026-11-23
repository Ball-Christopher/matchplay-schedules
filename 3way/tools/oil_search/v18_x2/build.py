"""Check a finished 34-week schedule (finish.py's .raw.json) from its weeks alone and
write 3way/v18_oil_x2.json / .toml.   usage: build.py out/fin.raw.json"""
import sys, json, itertools, os
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); D3 = os.path.join(HERE, "../../..")
raw = json.load(open(sys.argv[1])); flat = raw["weeks"]
r1 = json.load(open(os.path.join(D3, "v18_oil.json")))["weeks"]
v, n, k = 18, 6, 3; BL = [8, 5, 6, 7, 8]
assert len(flat) == 34 and flat[:17] == r1, "round 1 not preserved"
W = [[w[i:i+3] for i in range(0, 18, 3)] for w in flat]
P = list(itertools.combinations(range(1, v + 1), 2))
pr = lambda wk: [tuple(sorted(e)) for g in wk for e in itertools.combinations(g, 2)]
assert all(sorted(w) == list(range(1, v + 1)) for w in flat)
cuts = [0] + list(itertools.accumulate(BL))
for a, b in zip(cuts, cuts[1:]):
    c = Counter(e for wk in W[a:b] for e in pr(wk)); assert max(c.values()) == 1, f"clash in block {a+1}-{b}"
c2 = Counter(e for wk in W[17:] for e in pr(wk)); assert all(c2[e] == 2 for e in P), "round 2 not a 2-design"
m = Counter(); sp = []
for wk in W:
    m.update(pr(wk)); sp.append(max(m[e] for e in P) - min(m[e] for e in P))
assert all(m[e] == 4 for e in P)
lane = Counter(); pos = Counter(); ppre = []
for wk in W:
    for l, g in enumerate(wk):
        for q, p in enumerate(g): lane[p, l] += 1; pos[p, q] += 1
    ppre.append(max(max(pos[p, q] for q in range(3)) - min(pos[p, q] for q in range(3)) for p in range(1, v + 1)))
assert all(5 <= lane[p, l] <= 6 for p in range(1, v + 1) for l in range(n)), "lanes"
assert all(11 <= pos[p, q] <= 12 for p in range(1, v + 1) for q in range(3)) and max(ppre) <= 1, "positions"
t1 = Counter(tuple(sorted(g)) for wk in W[:17] for g in wk); t2 = Counter(tuple(sorted(g)) for wk in W[17:] for g in wk)
rep = sorted(t for t in t2 if t in t1); within2 = sum(c - 1 for c in t2.values())
join = len({tuple(sorted(g)) for g in W[16]} & {tuple(sorted(g)) for g in W[17]})
same_lane_join = sum(1 for p in range(1, v + 1) if [p in g for g in W[16]].index(True) == [p in g for g in W[17]].index(True))
print("blocks", BL, "all clash-free; round 2 a resolvable 2-(18,3,2); couples 4x")
print("prefix spread", sp); print("position prefix spread max", max(ppre))
print("trios of round 2 also in round 1:", len(rep), rep, "| trios repeated within round 2:", within2, "| at join:", join)
method = ("Round 1 = v18_oil exactly (blocks 8, 5, 4). Round 2 = X (2 weeks) + Y (7 weeks) + Z (8 weeks): X+Y is a resolvable minimum "
  "covering of K18 by 9 classes whose doubled couples form a 1-factor F', each F' couple once in X and once in Y; Z is round 1's "
  "nearly Kirkman triple system relabelled so that its missing 1-factor is F'. X is clash-free against round 1's last 4 weeks, so "
  "the five blocks are 8, 5, 4+2, 7, 8 (the optimum: a clash-free run has at most 8 weeks). The covering was found by z3 with a "
  "prescribed fixed-point-free order-3 automorphism (X = 2 invariant weeks; Y = a 3-week orbit + 4 invariant weeks, with X + the "
  "first 5 weeks of Y clash-free so F' recurs only in Y's last 2 weeks), then relabelled: two couple-disjoint weeks are a cubic "
  "bipartite graph on 6+6 trios whose 18 edges are the bowlers, and the 34 admissible week pairs in the complement of round 1's "
  "last block (clash-free, one week transversal to the positions the bowlers are owed after 17 weeks) were matched to X by graph "
  "isomorphism, keeping the isomorphism with fewest round-1 trios. Z's relabelling by hill-climb (no repeated trio). Lanes of round 2 "
  "by z3 (QF_FD) against round 1's counts: every bowler 5 or 6 times on every lane pair over 34 weeks. Positions: round 1 unchanged, "
  "week 18 gives each bowler the position they are owed, weeks 19-34 by de Werra edge colouring; within one of even after every week. "
  f"Prefix spread 2 only at week 25 (and round 1's weeks 9-10); {len(rep)} round-2 trios also occur in round 1.")
out = {"players": v, "group": k, "rounds": 2, "lambda": 4, "weeks": flat, "blocks": BL, "lane_balance_exact": True,
       "lane_off_bowlers": 0,
       "lane_counts": {str(p): [lane[p, l] for l in range(n)] for p in range(1, v + 1)},
       "position_counts": {str(p): [pos[p, q] for q in range(3)] for p in range(1, v + 1)},
       "prefix_spread": sp, "method": method}
json.dump(out, open(os.path.join(D3, "v18_oil_x2.json"), "w"), indent=1)
with open(os.path.join(D3, "v18_oil_x2.toml"), "w") as f:
    f.write("# 18 bowlers, groups of 3, two rounds (34 weeks), every couple meets exactly 4 times (twice per round).\n")
    f.write("# Weeks 1-17 are v18_oil unchanged.\n")
    f.write(f"# Oil-pattern blocks (weeks, in order): {BL} -- " + ", ".join(f"block {i+1} = weeks {cuts[i]+1}-{cuts[i+1]}" for i in range(5)) + ".\n")
    f.write("# Within a block no couple shares a group twice, so each couple meets on 4 different patterns of the 5.\n")
    f.write(f"# Lane pairs = consecutive groups of 3 in each week; lane balance exact: true; positions balanced. Worst prefix spread {max(sp[:-1])}.\n")
    f.write(f"# Method: {method}\n")
    f.write("# Groups of 3 in lane-pair order from first_lane up; within a group: left lane 1st, right lane 1st, left lane 2nd.\n")
    f.write("[schedule]\nweeks = [\n" + "".join("  " + json.dumps(w) + ",\n" for w in flat) + "]\n")
print("wrote v18_oil_x2.json/.toml")
