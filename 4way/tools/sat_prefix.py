"""z3 model: full resolvable 2-(v,4,3) schedule whose prefixes have bounded spread.
usage: python3 sat_prefix.py v timeout_s spreads   (spreads = comma list s_1..s_r;
s_W=1 forces the exact band floor/ceil(3W/(v-1)); s_W>=2 lets z3 pick the window)."""
import json, math, sys, time
from itertools import combinations
from z3 import Bool, Int, Solver, And, Or, Implies, PbEq, PbLe, PbGe, sat, Sum, If
v = int(sys.argv[1]); tl = int(sys.argv[2]); lam = 3
n = v // 4; r = lam * (v - 1) // 3
LANES = "--lanes" in sys.argv
sys.argv = [a for a in sys.argv if a != "--lanes"]
sp = list(map(int, sys.argv[3].split(","))) if len(sys.argv) > 3 else [1] * r
x = [[[Bool(f"x{w}_{p}_{g}") for g in range(n)] for p in range(v)] for w in range(r)]
S = Solver(); S.set("timeout", tl * 1000); S.set("random_seed", int(sys.argv[4]) if len(sys.argv) > 4 else 0)
for w in range(r):
    for p in range(v):
        S.add(PbEq([(x[w][p][g], 1) for g in range(n)], 1))
    for g in range(n):
        S.add(PbEq([(x[w][p][g], 1) for p in range(v)], 4))
    if LANES: continue
    S.add(x[w][0][0])
    for p in range(1, v):
        for g in range(1, n):
            S.add(Implies(x[w][p][g], Or([x[w][q][g-1] for q in range(p)])))
for p in range(v):
    S.add(x[0][p][p // 4])
if LANES:
    lo_, hi_ = r // n, -(-r // n)
    for p in range(v):
        for g in range(n):
            lits = [(x[w][p][g], 1) for w in range(r)]
            S.add(PbLe(lits, hi_)); S.add(PbGe(lits, lo_))
m = {}
L = {W: Int(f"L{W}") for W in range(1, r + 1)}
for a, b in combinations(range(v), 2):
    for w in range(r):
        mv = Bool(f"m{w}_{a}_{b}"); m[(w, a, b)] = mv
        S.add(mv == Or([And(x[w][a][g], x[w][b][g]) for g in range(n)]))
    for W in range(1, r + 1):
        lits = [(m[(w, a, b)], 1) for w in range(W)]
        if W == r:
            S.add(PbEq(lits, lam)); continue
        if sp[W-1] <= 1:
            lo = math.floor(lam * W / (v - 1)); hi = math.ceil(lam * W / (v - 1))
            S.add(PbLe(lits, hi))
            if lo > 0: S.add(PbGe(lits, lo))
        else:
            s = Sum([If(m[(w, a, b)], 1, 0) for w in range(W)])
            S.add(s >= L[W], s <= L[W] + sp[W-1])
t0 = time.time(); res = S.check(); print(res, round(time.time() - t0, 1), "s", flush=True)
if res == sat:
    M = S.model()
    weeks = [[[p + 1 for p in range(v) if M.evaluate(x[w][p][g])] for g in range(n)] for w in range(r)]
    tag = "".join(map(str, sp)) + ("L" if LANES else "")
    json.dump({"weeks": weeks, "spreads_target": sp}, open(f"sat_v{v}_{tag}.json", "w"))
