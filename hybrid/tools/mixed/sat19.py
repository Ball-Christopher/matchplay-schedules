"""v=19, mix 0/3/4 in 7 weeks: 3 A-weeks (5 triples + 1 quad), 4 B-weeks (1 triple + 4 quads).
sat_p0.py shows no bowler can be in two A-quads (cases x0=2, x0=3 unsat), so the A-quads are disjoint,
the B-triples are disjoint, both cover the same 12 bowlers U, and U is a 3x4 grid: A-quad i = row i, B-triple j = column j.
This model fixes that grid (bowlers 0..11 = (i,j) -> 4i+j; Z = 12..18) and asks z3 for the rest.
Optional case split on how the 7 other bowlers Z sit in A-week 0 fixes their labels (removes most Z symmetry).
Proof that 19 in 7 weeks (0/3/4) is impossible (z3 runs of 24 Nov 2026, logs/g/):
 sat_p0.py x0=3 unsat (11 s), x0=2 unsat (1436 s)  => every bowler in at most one A-quad => grid above.
 A-week triples hold <= 2 U-bowlers (only two rows available), so A-week Z-content is (0,3,2,0) or (0,4,0,1) [n0..n3 =
 triples with 0..3 Z]; case 0,4,0,1 unsat (1586 s), so by row symmetry every A-week is 0,3,2,0. Counting couples among Z
 (21) and diagonal U-couples (36) then forces three B-weeks with quads holding 3,2,1,1 Z-bowlers and one with 2,2,2,1;
 by column symmetry B-week 0 can be a 3,2,1,1 week: case "0,3,2,0 0,1,1" unsat (574 s). ("0,3,2,0 1,0,0" unsat, 182 s.)
usage: sat19.py timeout [n0,n1,n2,n3 [q4,q3,q2 ...]]  (q4,q3,q2 per B-week in order)   (optional case: Z-content of A-week 0 triples; Z labels fixed accordingly)"""
import sys, itertools, json, z3, time
tmo = int(sys.argv[1]); v = 19
U = [(i, j) for i in range(3) for j in range(4)]; uid = {u: 4 * u[0] + u[1] for u in U}; Z = list(range(12, 19))
weeks = [("A", i) for i in range(3)] + [("B", j) for j in range(4)]
fixed = {}
for k, (t, i) in enumerate(weeks):
    fixed[k] = [uid[(i, j)] for j in range(4)] if t == "A" else [uid[(r, i)] for r in range(3)]
S = z3.SolverFor("QF_FD"); S.set("timeout", tmo * 1000)
X = {}; pairv = {pq: [] for pq in itertools.combinations(range(v), 2)}
for k, (t, i) in enumerate(weeks):
    F = set(fixed[k]); s, cnt = (3, 5) if t == "A" else (4, 4)
    rest = [p for p in range(v) if p not in F]; lits = []; inc = {p: [] for p in rest}
    for B in itertools.combinations(rest, s):
        x = z3.Bool(f"x{k}_{'_'.join(map(str, B))}"); X[k, B] = x; lits.append(x)
        for p in B: inc[p].append((x, 1))
        for pq in itertools.combinations(B, 2): pairv[pq].append(x)
    S.add(z3.PbEq([(l, 1) for l in lits], cnt))
    for p in rest: S.add(z3.PbEq(inc[p], 1))
    for pq in itertools.combinations(sorted(F), 2): pairv[pq].append(True)
for pq, l in pairv.items():
    f = sum(1 for x in l if x is True); lits = [(x, 1) for x in l if x is not True]
    assert f <= 1
    S.add(z3.PbEq(lits, 1 - f) if lits else z3.BoolVal(f == 1))
if len(sys.argv) > 2:
    n0, n1, n2, n3 = map(int, sys.argv[2].split(",")); zs = []; z = 12
    for size, cnt in ((3, n3), (2, n2), (1, n1), (0, n0)):
        for _ in range(cnt): zs.append(list(range(z, z + size))); z += size
    assert z == 19 and len(zs) == 5
    rows12 = [p for p in range(12) if p // 4 != 0]
    for zp in zs:  # some chosen triple of A-week 0 has exactly this Z-part
        cands = [x for (k, B), x in X.items() if k == 0 and [p for p in B if p >= 12] == zp]
        S.add(z3.Or(cands))
for kb, arg in enumerate(sys.argv[3:]):  # B-week kb split: number of quads with 4, 3, 2 Z-bowlers
    for nz, c in zip((4, 3, 2), map(int, arg.split(","))):
        S.add(z3.PbEq([(x, 1) for (k, B), x in X.items() if k == 3 + kb and sum(1 for p in B if p >= 12) == nz], c))
t0 = time.time(); r = S.check(); print(r, f"{time.time()-t0:.1f}s", file=sys.stderr)
if r == z3.sat:
    M = S.model()
    out = [[[q + 1 for q in fixed[k]]] + [[q + 1 for q in B] for (kk, B), x in X.items() if kk == k and z3.is_true(M[x])] for k in range(7)]
    print(json.dumps(out))
else: sys.exit(1)
