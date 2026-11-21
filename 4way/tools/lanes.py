#!/usr/bin/env python3
"""Lane-pair balance: permute the groups inside each week (pair balance unchanged) so
each bowler is on each lane pair floor(r/n) or ceil(r/n) times. z3 pseudo-Boolean
model (system python3); week 0 kept in place to break symmetry."""
import sys
from z3 import Bool, Solver, PbEq, PbLe, PbGe, sat, is_true

def balance_lanes(weeks, timeout_s=300, ignore=()):
    r = len(weeks); n = len(weeks[0])
    v = sum(len(g) for g in weeks[0])
    lo, hi = r // n, -(-r // n)
    y = [[[Bool(f"y{w}_{g}_{l}") for l in range(n)] for g in range(n)] for w in range(r)]
    S = Solver(); S.set("timeout", timeout_s * 1000)
    for w in range(r):
        for g in range(n):
            S.add(PbEq([(y[w][g][l], 1) for l in range(n)], 1))
        for l in range(n):
            S.add(PbEq([(y[w][g][l], 1) for g in range(n)], 1))
    for g in range(n):
        S.add(y[0][g][g])
    gof = {}
    for w, wk in enumerate(weeks):
        for g, G in enumerate(wk):
            for p in G:
                gof[(w, p)] = g
    players = sorted({p for G in weeks[0] for p in G} - set(ignore))
    for p in players:
        for l in range(n):
            lits = [(y[w][gof[(w, p)]][l], 1) for w in range(r)]
            S.add(PbLe(lits, hi))
            if lo > 0:
                S.add(PbGe(lits, lo))
    res = S.check()
    if res != sat:
        return None, str(res)
    M = S.model()
    out = []
    for w in range(r):
        row = [None] * n
        for g in range(n):
            for l in range(n):
                if is_true(M.evaluate(y[w][g][l])):
                    row[l] = weeks[w][g]
        out.append(row)
    return out, "sat"

def lane_counts(weeks):
    n = len(weeks[0]); cnt = {}
    for wk in weeks:
        for l, G in enumerate(wk):
            for p in G:
                cnt.setdefault(p, [0] * n)[l] += 1
    return cnt

def balance_lanes_opt(weeks, timeout_s=300, excess_first=False, ignore=()):
    """Fallback when exact is infeasible: minimise (bowlers off, total excess)."""
    from z3 import Optimize, Int, If, Sum, Or, is_true
    r = len(weeks); n = len(weeks[0])
    lo, hi = r // n, -(-r // n)
    y = [[[Bool(f"y{w}_{g}_{l}") for l in range(n)] for g in range(n)] for w in range(r)]
    O = Optimize(); O.set("timeout", timeout_s * 1000)
    for w in range(r):
        for g in range(n):
            O.add(PbEq([(y[w][g][l], 1) for l in range(n)], 1))
        for l in range(n):
            O.add(PbEq([(y[w][g][l], 1) for g in range(n)], 1))
    for g in range(n):
        O.add(y[0][g][g])
    gof = {}
    for w, wk in enumerate(weeks):
        for g, G in enumerate(wk):
            for p in G:
                gof[(w, p)] = g
    players = sorted({p for G in weeks[0] for p in G} - set(ignore))
    offs, exc = [], []
    for p in players:
        off = Bool(f"off{p}"); offs.append(off)
        for l in range(n):
            c = Sum([If(y[w][gof[(w, p)]][l], 1, 0) for w in range(r)])
            e = Int(f"e{p}_{l}"); exc.append(e)
            O.add(e >= 0, e >= c - hi, e >= lo - c)
            O.add(If(off, True, e == 0))
    objs = [Sum([If(o, 1, 0) for o in offs]), Sum(exc)]
    if excess_first:
        objs.reverse()
    for ob in objs:
        O.minimize(ob)
    res = O.check()
    M = O.model()
    out = []
    for w in range(r):
        row = [None] * n
        for g in range(n):
            for l in range(n):
                if is_true(M.evaluate(y[w][g][l])):
                    row[l] = weeks[w][g]
        out.append(row)
    return out, str(res)

def balance_lanes_next(weeks, prev, timeout_s=300):
    """Lane order for a following cycle of the same weeks: cumulative counts
    (prev + this cycle) must sit in the floor/ceil band for the total number of
    weeks (hard); then minimise bowlers outside the band for this cycle alone."""
    from z3 import Optimize, If, Sum, Or, Not, is_true
    r = len(weeks); n = len(weeks[0])
    R = r + sum(prev[next(iter(prev))])
    lo, hi = r // n, -(-r // n)
    LO, HI = R // n, -(-R // n)
    y = [[[Bool(f"y{w}_{g}_{l}") for l in range(n)] for g in range(n)] for w in range(r)]
    O = Optimize(); O.set("timeout", timeout_s * 1000)
    for w in range(r):
        for g in range(n):
            O.add(PbEq([(y[w][g][l], 1) for l in range(n)], 1))
        for l in range(n):
            O.add(PbEq([(y[w][g][l], 1) for g in range(n)], 1))
    gof = {(w, p): g for w, wk in enumerate(weeks) for g, G in enumerate(wk) for p in G}
    offs = []
    for p in sorted(prev):
        conds = []
        for l in range(n):
            lits = [(y[w][gof[(w, p)]][l], 1) for w in range(r)]
            O.add(PbLe(lits, HI - prev[p][l]))
            if LO - prev[p][l] > 0:
                O.add(PbGe(lits, LO - prev[p][l]))
            conds += [PbLe(lits, hi), PbGe(lits, lo)]
        off = Bool(f"off{p}"); offs.append(off)
        O.add(Or(off, *[]) if False else Or(off, And_(conds)))
    O.minimize(Sum([If(o, 1, 0) for o in offs]))
    res = O.check()
    if res != sat:
        return None, str(res)
    M = O.model()
    out = []
    for w in range(r):
        row = [None] * n
        for g in range(n):
            for l in range(n):
                if is_true(M.evaluate(y[w][g][l])):
                    row[l] = weeks[w][g]
        out.append(row)
    return out, "sat"

def And_(xs):
    from z3 import And
    return And(*xs)

def balance_lanes_anneal(weeks, seconds=60, seed=0, ignore=()):
    """Simulated annealing over within-week group orders (swap two lane pairs in a
    week). Cost = total distance of counts outside the floor/ceil band."""
    import random, math, time
    rng = random.Random(seed)
    r = len(weeks); n = len(weeks[0])
    lo, hi = r // n, -(-r // n)
    W = [list(map(list, wk)) for wk in weeks]
    cnt = lane_counts(W)
    for p in ignore:
        cnt[p] = [lo] * n  # never charged: kept constant in band
    def f(c): return 0 if c is None else (lo - c if c < lo else (c - hi if c > hi else 0))
    ign = set(ignore)
    cost = sum(f(c) for v in cnt.values() for c in v)
    best = (cost, [list(map(list, wk)) for wk in W])
    T = 1.0; t0 = time.time()
    while cost and time.time() - t0 < seconds:
        w = rng.randrange(1, r); a, b = rng.sample(range(n), 2)
        d = 0
        for p in W[w][a]:
            if p in ign: continue
            d += f(cnt[p][a] - 1) - f(cnt[p][a]) + f(cnt[p][b] + 1) - f(cnt[p][b])
            cnt[p][a] -= 1; cnt[p][b] += 1
        for p in W[w][b]:
            if p in ign: continue
            d += f(cnt[p][b] - 1) - f(cnt[p][b]) + f(cnt[p][a] + 1) - f(cnt[p][a])
            cnt[p][b] -= 1; cnt[p][a] += 1
        if d <= 0 or rng.random() < math.exp(-d / T):
            W[w][a], W[w][b] = W[w][b], W[w][a]; cost += d
            if cost < best[0]:
                best = (cost, [list(map(list, wk)) for wk in W])
        else:
            for p in W[w][a]:
                if p not in ign: cnt[p][a] += 1; cnt[p][b] -= 1
            for p in W[w][b]:
                if p not in ign: cnt[p][b] += 1; cnt[p][a] -= 1
        T = max(0.2, T * 0.99999)
    return best[1], best[0]

def balance_lanes_glpk(weeks, timeout_s=300, workdir="."):
    """Same exact model as balance_lanes, solved as a 0/1 ILP by glpsol
    (minimise total excess outside the band, so a best-effort answer comes back
    on timeout). Returns (weeks, excess or None)."""
    import subprocess, os, re
    r = len(weeks); n = len(weeks[0])
    lo, hi = r // n, -(-r // n)
    gof = {(w, p): g for w, wk in enumerate(weeks) for g, G in enumerate(wk) for p in G}
    players = sorted({p for G in weeks[0] for p in G} - set(ignore))
    lp = ["Minimize", " obj: " + " + ".join(f"u{p}_{l} + d{p}_{l}" for p in players for l in range(n)), "Subject To"]
    for w in range(r):
        for g in range(n):
            lp.append(f" a{w}_{g}: " + " + ".join(f"y{w}_{g}_{l}" for l in range(n)) + " = 1")
        for l in range(n):
            lp.append(f" b{w}_{l}: " + " + ".join(f"y{w}_{g}_{l}" for g in range(n)) + " = 1")
    for g in range(n):
        lp.append(f" fix{g}: y0_{g}_{g} = 1")
    for p in players:
        for l in range(n):
            s = " + ".join(f"y{w}_{gof[(w, p)]}_{l}" for w in range(r))
            lp.append(f" h{p}_{l}: {s} - u{p}_{l} <= {hi}")
            lp.append(f" k{p}_{l}: {s} + d{p}_{l} >= {lo}")
    lp.append("Binary")
    lp += [f" y{w}_{g}_{l}" for w in range(r) for g in range(n) for l in range(n)]
    lp.append("End")
    f = os.path.join(workdir, "_lanes.lp"); o = os.path.join(workdir, "_lanes.sol")
    open(f, "w").write("\n".join(lp) + "\n")
    vals = {}
    o2 = o + ".txt"
    subprocess.run(["/opt/homebrew/bin/glpsol", "--lp", f, "--tmlim", str(timeout_s), "-o", o2],
                   stdout=subprocess.DEVNULL)
    txt = open(o2).read()
    for m in re.finditer(r"^\s*\d+\s+(y\d+_\d+_\d+)\s+\*\s+(\d)", txt, re.M):
        vals[m.group(1)] = int(m.group(2))
    if not vals:
        return None, None
    out = []
    for w in range(r):
        row = [None] * n
        for g in range(n):
            for l in range(n):
                if vals.get(f"y{w}_{g}_{l}"):
                    row[l] = weeks[w][g]
        out.append(row)
    if any(x is None for row in out for x in row):
        return None, None
    cnt = lane_counts(out)
    exc = sum(max(0, c - hi) + max(0, lo - c) for v in cnt.values() for c in v)
    for p in (f, o, o2):
        if os.path.exists(p): os.remove(p)
    return out, exc

def balance_lanes_lns(weeks, seconds=300, k=4, seed=0, start=None, log=False):
    """Large-neighbourhood search: start from annealing, then repeatedly free k
    random weeks and re-solve their lane orders exactly with z3 (minimise total
    excess outside the band, other weeks fixed). Returns (weeks, excess)."""
    import random, time
    from z3 import Optimize, If, Sum, Int, is_true
    rng = random.Random(seed)
    r = len(weeks); n = len(weeks[0])
    lo, hi = r // n, -(-r // n)
    W, _ = (start, None) if start else balance_lanes_anneal(weeks, 30, seed)
    W = [list(map(list, wk)) for wk in W]
    def excess(W):
        cnt = lane_counts(W)
        return sum(max(0, c - hi) + max(0, lo - c) for v in cnt.values() for c in v)
    cur = excess(W); t0 = time.time()
    while cur and time.time() - t0 < seconds:
        free = rng.sample(range(r), k)
        fixed = [W[w] for w in range(r) if w not in free]
        base = lane_counts(fixed) if fixed else {}
        O = Optimize(); O.set("timeout", 20000)
        y = {(w, g, l): Bool(f"y{w}_{g}_{l}") for w in free for g in range(n) for l in range(n)}
        for w in free:
            for g in range(n):
                O.add(PbEq([(y[(w, g, l)], 1) for l in range(n)], 1))
            for l in range(n):
                O.add(PbEq([(y[(w, g, l)], 1) for g in range(n)], 1))
        gof = {(w, p): g for w in free for g, G in enumerate(W[w]) for p in G}
        exc = []
        for p in sorted(lane_counts(W)):
            for l in range(n):
                c = base.get(p, [0] * n)[l] + Sum([If(y[(w, gof[(w, p)], l)], 1, 0) for w in free])
                e = Int(f"e{p}_{l}"); O.add(e >= 0, e >= c - hi, e >= lo - c); exc.append(e)
        O.minimize(Sum(exc))
        if O.check() == sat:
            M = O.model()
            new = [list(map(list, wk)) for wk in W]
            for w in free:
                row = [None] * n
                for g in range(n):
                    for l in range(n):
                        if is_true(M.evaluate(y[(w, g, l)])):
                            row[l] = W[w][g]
                new[w] = row
            e = excess(new)
            if e <= cur:
                W, cur = new, e
                if log: print("  lns excess", cur, round(time.time() - t0), flush=True)
    return W, cur
