#!/usr/bin/env python3
"""Generate balanced 3-way matchplay schedules (resolvable 2-(v,3,lambda) designs).

Construction (all cases): points Z_n x {0..m-1} plus infinity, with n odd.
A set of c base parallel classes is found by randomised backtracking so that
every "difference" (level i, level j, d) is covered exactly lambda times and
infinity meets each level lambda times.  Developing each base class over Z_n
gives c*n = r weeks.

  v=15: n=7,  m=2, c=1, lambda=1  (Kirkman triple system, 7 weeks)
  v=21: n=5,  m=4, c=2, lambda=1  (KTS, 10 weeks)
  v=27: n=13, m=2, c=1, lambda=1  (KTS, 13 weeks)
  v=12: n=11, m=1, c=1, lambda=2  (1-rotational over Z_11, 11 weeks)
  v=18: n=17, m=1, c=1, lambda=2  (17 weeks)
  v=24: n=23, m=1, c=1, lambda=2  (23 weeks)

Then: simulated annealing over within-week group order for lane balance, and
over week order for prefix pair balance.  For lambda=2 many base classes are
tried and the one with the best prefix profile is kept.

Usage: python3 gen.py [v ...]
"""
import json
import random
import sys
import time
from itertools import combinations
from pathlib import Path

OUT = Path(__file__).resolve().parent

PARAMS = {15: (7, 2, 1, 1), 21: (5, 4, 2, 1), 27: (13, 2, 1, 1),
          12: (11, 1, 1, 2), 18: (17, 1, 1, 2), 24: (23, 1, 1, 2)}


# ---------------------------------------------------------------- design
def find_base_classes(v, rng, node_limit=200000, min_offset=None, mixed=False):
    """min_offset (lambda=2, m=1 only): the two occurrences of each difference
    (and the two infinity pairs) must come from starts whose cyclic distance is
    >= min_offset.  Then shifts 0..K-1 (K=min_offset) are pair-disjoint and
    shifts 0..n-K-1 cover every pair, so only prefixes K+1..n-K-1 have spread 2."""
    n, m, c, lam = PARAMS[v]
    first = {}
    # mixed (m=2): every block meets both levels, so with base block j on lane
    # pair j each finite bowler lands on every lane pair 1-2 times (vacancy files)

    def far(a, b):
        e = (b - a) % n
        return min(e, n - e) >= min_offset
    INF = -1
    finite = [(i, a) for i in range(m) for a in range(n)]
    need = {}
    for i in range(m):
        for j in range(m):
            for d in range(n):
                if i == j and d == 0:
                    continue
                need[(i, j, d)] = lam
    inf_need = [lam] * m
    nodes = [0]

    def pair_keys(p, q):
        (i, a), (j, b) = p, q
        return [(i, j, (b - a) % n), (j, i, (a - b) % n)]

    def can_add(p, q):
        ks = pair_keys(p, q)
        if ks[0] == ks[1]:
            return need[ks[0]] >= 2
        if not (need[ks[0]] >= 1 and need[ks[1]] >= 1):
            return False
        if min_offset is not None:
            for k, start in zip(ks, (p[1], q[1])):
                if need[k] == 1 and not far(first[k], start):
                    return False
        return True

    def apply(p, q, s):
        for k, start in zip(pair_keys(p, q), (p[1], q[1])):
            if s == 1 and need[k] == lam:
                first[k] = start
            need[k] -= s

    classes = []

    def solve_class(k, unused, blocks):
        nodes[0] += 1
        if nodes[0] > node_limit:
            raise TimeoutError
        if not unused:
            classes.append(list(blocks))
            if k + 1 == c:
                return True
            if solve_class(k + 1, set(finite) | {INF}, []):
                return True
            classes.pop()
            return False
        if INF in unused:
            cand = [x for x in unused if x != INF]
            rng.shuffle(cand)
            for p, q in combinations(cand, 2):
                if inf_need[p[0]] < 1 or inf_need[q[0]] < 1:
                    continue
                if p[0] == q[0] and inf_need[p[0]] < 2:
                    continue
                if min_offset is not None and not far(p[1], q[1]):
                    continue
                if mixed and p[0] == q[0]:
                    continue
                if not can_add(p, q):
                    continue
                inf_need[p[0]] -= 1; inf_need[q[0]] -= 1; apply(p, q, 1)
                blocks.append((INF, p, q))
                if solve_class(k, unused - {INF, p, q}, blocks):
                    return True
                blocks.pop()
                inf_need[p[0]] += 1; inf_need[q[0]] += 1; apply(p, q, -1)
            return False
        x = min(unused)
        rest = [y for y in unused if y != x]
        rng.shuffle(rest)
        for p, q in combinations(rest, 2):
            if not can_add(x, p):
                continue
            if mixed and x[0] == p[0] == q[0]:
                continue
            apply(x, p, 1)
            if not can_add(x, q):
                apply(x, p, -1)
                continue
            apply(x, q, 1)
            if not can_add(p, q):
                apply(x, p, -1); apply(x, q, -1)
                continue
            apply(p, q, 1)
            blocks.append((x, p, q))
            if solve_class(k, unused - {x, p, q}, blocks):
                return True
            blocks.pop()
            apply(x, p, -1); apply(x, q, -1); apply(p, q, -1)
        return False

    try:
        ok = solve_class(0, set(finite) | {INF}, [])
    except TimeoutError:
        return None
    if not ok:
        return None
    assert all(x == 0 for x in need.values()) and all(x == 0 for x in inf_need)
    return classes


def develop(v, classes):
    n, m, c, lam = PARAMS[v]

    def label(p, t):
        if p == -1:
            return v
        i, a = p
        return i * n + (a + t) % n + 1

    weeks = []
    for cl in classes:
        for t in range(n):
            weeks.append([sorted(label(p, t) for p in b) for b in cl])
    return weeks


def one_rotational_kts(v, rng, budget=120, gaps=False):
    """1-rotational KTS(v) under Z_{2n}, 2n = v-1: base class
    {inf, x, x+n} + B_i + (B_i + n), i=1..(v-3)/6, where the B_i's differences cover
    Z_{2n} minus {0, n} once.  Developing s = 0..n-1 gives the n weeks.  Optional
    condition (gaps=True): no B_i fits inside n consecutive residues, which would
    make fixed lanes balance every finite bowler (none found for v=27 in 150 s).
    Exhaustive search finds none at all for v=15, 21 (consistent with cyclic
    1-rotational KTS(v) needing v = 3 mod 24).  Returns (x, [B_i]) or None."""
    N = v - 1
    n = N // 2
    k = (v - 3) // 6
    deadline = time.time() + budget

    def ok_gaps(t):
        a = sorted(t)
        gaps = [a[1] - a[0], a[2] - a[1], N - a[2] + a[0]]
        return max(gaps) <= n

    while time.time() < deadline:
        x = 0  # translate so the infinity block is {inf, 0, n}
        used = {0, n}
        diffs = set()
        blocks = []

        def rec():
            if time.time() > deadline:
                return False
            if len(blocks) == k:
                return True
            free = [z for z in range(N) if z not in used]
            a = min(free)
            rest = [z for z in free if z != a and (z + n) % N not in used and z != (a + n) % N]
            rng.shuffle(rest)
            for b, c in combinations(rest, 2):
                t = (a, b, c)
                pts = set(t) | {(z + n) % N for z in t}
                if len(pts) != 6 or pts & used:
                    continue
                ds = [(p - q) % N for p in t for q in t if p != q]
                if len(set(ds)) != 6 or set(ds) & diffs or n in ds:
                    continue
                if gaps and not ok_gaps(t):
                    continue
                used.update(pts); diffs.update(ds); blocks.append(t)
                if rec():
                    return True
                blocks.pop(); used.difference_update(pts); diffs.difference_update(ds)
            return False

        if rec():
            return x, blocks
    return None


def develop_1rot(v, blocks):
    N = v - 1
    n = N // 2
    base = [(-1, 0, n)]
    for t in blocks:
        base.append(t)
        base.append(tuple((z + n) % N for z in t))
    weeks = []
    for s in range(n):
        weeks.append([sorted(v if z == -1 else (z + s) % N + 1 for z in b) for b in base])
    return weeks, base


# ---------------------------------------------------------------- prefix order
def pair_index(v):
    idx = {}
    for a, b in combinations(range(1, v + 1), 2):
        idx[(a, b)] = len(idx)
    return idx


def week_pairs(week, idx):
    out = []
    for g in week:
        for a, b in combinations(sorted(g), 2):
            out.append(idx[(a, b)])
    return out


def prefix_profile(order, wp, npairs):
    cnt = [0] * npairs
    spreads, sq = [], 0
    for w in order:
        for p in wp[w]:
            sq += 2 * cnt[p] + 1
            cnt[p] += 1
        spreads.append(max(cnt) - min(cnt))
        sq_w = sq
    return spreads


def order_cost(order, wp, npairs):
    """(#prefixes with spread>=2, max spread, sum over prefixes of sum c^2)"""
    cnt = [0] * npairs
    sq = 0
    tot_sq = 0
    bad = 0
    worst = 0
    zeros = npairs
    for w in order:
        for p in wp[w]:
            if cnt[p] == 0:
                zeros -= 1
            sq += 2 * cnt[p] + 1
            cnt[p] += 1
        mx = max(cnt)
        mn = 0 if zeros else min(cnt)
        s = mx - mn
        worst = max(worst, s)
        if s >= 2:
            bad += 1
        tot_sq += sq
    return (worst, bad, tot_sq)


def optimise_order(weeks, v, rng, iters=20000):
    idx = pair_index(v)
    npairs = len(idx)
    wp = [week_pairs(w, idx) for w in weeks]
    r = len(weeks)
    order = list(range(r))
    cur = order_cost(order, wp, npairs)
    best, best_order = cur, order[:]
    T0 = 50.0
    for it in range(iters):
        T = T0 * (1 - it / iters) + 0.01
        i, j = rng.sample(range(r), 2)
        new = order[:]
        if rng.random() < 0.5:
            new[i], new[j] = new[j], new[i]
        else:
            x = new.pop(i); new.insert(j, x)
        nc = order_cost(new, wp, npairs)
        f = lambda c: c[0] * 10**7 + c[1] * 10**4 + c[2] / 10
        d = f(nc) - f(cur)
        if d <= 0 or rng.random() < pow(2.718, -d / T):
            order, cur = new, nc
            if f(cur) < f(best):
                best, best_order = cur, order[:]
    return [weeks[k] for k in best_order], best


# ---------------------------------------------------------------- lanes
def lane_cost_counts(weeks, v, perms):
    nl = v // 3
    cnt = [[0] * nl for _ in range(v + 1)]
    for w, perm in zip(weeks, perms):
        for lane, g in enumerate(perm):
            for p in w[g]:
                cnt[p][lane] += 1
    return cnt


def optimise_lanes(weeks, v, rng, iters=400000, restarts=8, frozen=0, players=None):
    """frozen: the first `frozen` weeks keep their order.  players: only these
    players count towards the penalty (default all)."""
    nl = v // 3
    r = len(weeks)
    lo, hi = r // nl, -(-r // nl)

    live = set(players or range(1, v + 1))

    def pen(c):
        return max(0, c - hi) + max(0, lo - c)

    def penp(p, c):
        return pen(c) if p in live else 0

    ident = lane_cost_counts(weeks, v, [list(range(nl))] * r)
    if all(penp(p, c) == 0 for p in range(1, v + 1) for c in ident[p]):
        return [list(w) for w in weeks], 0
    best_perms, best_cost = None, None
    for rs in range(restarts):
        # restart 0 starts from the given order: for a developed cyclic design that
        # puts every finite player exactly in balance, leaving only infinity to fix
        perms = [list(range(nl)) if (rs == 0 or w < frozen) else rng.sample(range(nl), nl)
                 for w in range(r)]
        cnt = lane_cost_counts(weeks, v, perms)
        cost = sum(penp(p, c) for p in range(1, v + 1) for c in cnt[p])
        T0 = 0.6 if rs == 0 else 2.0
        for it in range(iters):
            if cost == 0:
                break
            T = T0 * (1 - it / iters) + 0.05
            w = rng.randrange(frozen, r)
            a, b = rng.sample(range(nl), 2)
            ga, gb = weeks[w][perms[w][a]], weeks[w][perms[w][b]]
            d = 0
            for p in ga:
                d += (penp(p, cnt[p][a] - 1) - penp(p, cnt[p][a])
                      + penp(p, cnt[p][b] + 1) - penp(p, cnt[p][b]))
                cnt[p][a] -= 1; cnt[p][b] += 1
            for p in gb:
                d += (penp(p, cnt[p][b] - 1) - penp(p, cnt[p][b])
                      + penp(p, cnt[p][a] + 1) - penp(p, cnt[p][a]))
                cnt[p][b] -= 1; cnt[p][a] += 1
            if d <= 0 or rng.random() < pow(2.718, -d / T):
                perms[w][a], perms[w][b] = perms[w][b], perms[w][a]
                cost += d
                if best_cost is None or cost < best_cost:  # keep best state seen
                    best_cost, best_perms = cost, [p[:] for p in perms]
            else:
                for p in ga:
                    cnt[p][a] += 1; cnt[p][b] -= 1
                for p in gb:
                    cnt[p][b] += 1; cnt[p][a] -= 1
        if best_cost is None or cost < best_cost:
            best_cost, best_perms = cost, [p[:] for p in perms]
        if best_cost == 0:
            break
    ordered = [[w[g] for g in perm] for w, perm in zip(weeks, best_perms)]
    return ordered, best_cost


def z3_lanes(weeks, v, timeout_s=240, frozen=0):
    """Exact lane assignment with z3 (time-boxed). Returns reordered weeks or None."""
    try:
        import z3
    except ImportError:
        return None
    nl = v // 3
    r = len(weeks)
    lo, hi = r // nl, -(-r // nl)
    x = [[[z3.Bool(f"x{w}_{g}_{l}") for l in range(nl)] for g in range(nl)] for w in range(r)]
    s = z3.SolverFor("QF_FD")
    s.set("timeout", timeout_s * 1000)
    for w in range(r):
        for g in range(nl):
            s.add(z3.PbEq([(x[w][g][l], 1) for l in range(nl)], 1))
        for l in range(nl):
            s.add(z3.PbEq([(x[w][g][l], 1) for g in range(nl)], 1))
    for p in range(1, v + 1):
        occ = [(w, g) for w in range(r) for g in range(nl) if p in weeks[w][g]]
        for l in range(nl):
            terms = [(x[w][g][l], 1) for w, g in occ]
            s.add(z3.PbGe(terms, lo), z3.PbLe(terms, hi))
    for w in range(max(frozen, 1)):  # frozen weeks keep their order (week 0: symmetry)
        for g in range(nl):
            s.add(x[w][g][g])
    res = s.check()
    z3_lanes.last = str(res)
    if res != z3.sat:
        return None
    mdl = s.model()
    out = []
    for w in range(r):
        week = [None] * nl
        for g in range(nl):
            for l in range(nl):
                if z3.is_true(mdl.eval(x[w][g][l])):
                    week[l] = weeks[w][g]
        out.append(week)
    return out


def optimise_lanes_two(w1, w2, v, rng, iters=3000000, restarts=4):
    """Lane orders for two cycles at once: cycle 1 alone must be floor/ceil(r/n)
    and both together floor/ceil(2r/n).  Returns (w1', w2', penalty)."""
    nl = v // 3
    r = len(w1)
    lo1, hi1 = r // nl, -(-r // nl)
    lo2, hi2 = (2 * r) // nl, -(-(2 * r) // nl)
    weeks = w1 + w2

    def cellpen(a, b):
        return (max(0, a - hi1) + max(0, lo1 - a)) + (max(0, a + b - hi2) + max(0, lo2 - a - b))

    best = None
    for rs in range(restarts):
        perms = [list(range(nl)) if rs == 0 else rng.sample(range(nl), nl) for _ in weeks]
        A = lane_cost_counts(w1, v, perms[:r])
        B = lane_cost_counts(w2, v, perms[r:])
        cost = sum(cellpen(A[p][l], B[p][l]) for p in range(1, v + 1) for l in range(nl))
        for it in range(iters):
            if cost == 0:
                break
            T = 1.0 * (1 - it / iters) + 0.05
            w = rng.randrange(2 * r)
            C = A if w < r else B
            a, b = rng.sample(range(nl), 2)
            ga, gb = weeks[w][perms[w][a]], weeks[w][perms[w][b]]
            touched = {(p, a) for p in ga + gb} | {(p, b) for p in ga + gb}
            before = sum(cellpen(A[p][l], B[p][l]) for p, l in touched)
            for p in ga:
                C[p][a] -= 1; C[p][b] += 1
            for p in gb:
                C[p][b] -= 1; C[p][a] += 1
            d = sum(cellpen(A[p][l], B[p][l]) for p, l in touched) - before
            if d <= 0 or rng.random() < pow(2.718, -d / T):
                perms[w][a], perms[w][b] = perms[w][b], perms[w][a]
                cost += d
            else:
                for p in ga:
                    C[p][a] += 1; C[p][b] -= 1
                for p in gb:
                    C[p][b] += 1; C[p][a] -= 1
        if best is None or cost < best[0]:
            best = (cost, [p[:] for p in perms])
        if best[0] == 0:
            break
    cost, perms = best
    out = [[w[g] for g in perm] for w, perm in zip(weeks, perms)]
    return out[:r], out[r:], cost


# ---------------------------------------------------------------- second cycle
def second_cycle(weeks, v, rng, iters=300000, restarts=5):
    """Find a player relabelling sigma and lane-pair relabelling pi for cycle 2 so
    two-cycle lane totals are floor/ceil(2r/n) and the join week shares no group
    with cycle 1's last week.  In cycle 2, player sigma[p] bowls where p bowled
    in cycle 1, on lane pair pi[l] instead of l."""
    nl = v // 3
    r = len(weeks)
    c1 = lane_cost_counts(weeks, v, [list(range(nl))] * r)
    lo, hi = (2 * r) // nl, -(-(2 * r) // nl)

    def pen(c):
        return max(0, c - hi) + max(0, lo - c)

    last = {tuple(sorted(g)) for g in weeks[-1]}

    def join_clash(sig):
        first = {tuple(sorted(sig[p] for p in g)) for g in weeks[0]}
        return len(first & last)

    def term(p, sig, pi):
        q = sig[p]
        return sum(pen(c1[q][pi[l]] + c1[p][l]) for l in range(nl))

    # exact route: for a lane map pi, cycle-2 slot owner p can be relabelled to q
    # iff their summed counts are in range on every lane; that is a bipartite
    # perfect matching (augmenting paths), tried for many random lane maps.
    def matching(pi):
        ok = {p: [q for q in range(1, v + 1)
                  if all(pen(c1[q][pi[l]] + c1[p][l]) == 0 for l in range(nl))]
              for p in range(1, v + 1)}
        match = {}

        def aug(p, seen):
            for q in rng.sample(ok[p], len(ok[p])):
                if q in seen:
                    continue
                seen.add(q)
                if q not in match or aug(match[q], seen):
                    match[q] = p
                    return True
            return False

        for p in range(1, v + 1):
            if not aug(p, set()):
                return None
        sig = [0] * (v + 1)
        for q, p in match.items():
            sig[p] = q
        return sig

    t_end = time.time() + 60
    while time.time() < t_end:
        pi = rng.sample(range(nl), nl)
        sig = matching(pi)
        if sig is not None and not join_clash(sig):
            return {p: sig[p] for p in range(1, v + 1)}, pi, 0, 0

    best = None
    for rs in range(restarts):
        sig = [0] + rng.sample(range(1, v + 1), v)
        pi = rng.sample(range(nl), nl)
        lane = sum(term(p, sig, pi) for p in range(1, v + 1))
        for it in range(iters):
            if lane == 0:
                break
            T = 2.0 * (1 - it / iters) + 0.05
            if rng.random() < 0.05:
                i, j = rng.sample(range(nl), 2)
                pi[i], pi[j] = pi[j], pi[i]
                nlane = sum(term(p, sig, pi) for p in range(1, v + 1))
                if nlane <= lane or rng.random() < pow(2.718, -(nlane - lane) / T):
                    lane = nlane
                else:
                    pi[i], pi[j] = pi[j], pi[i]
                continue
            a, b = rng.sample(range(1, v + 1), 2)
            old = term(a, sig, pi) + term(b, sig, pi)
            sig[a], sig[b] = sig[b], sig[a]
            d = term(a, sig, pi) + term(b, sig, pi) - old
            if d <= 0 or rng.random() < pow(2.718, -d / T):
                lane += d
            else:
                sig[a], sig[b] = sig[b], sig[a]
        # fix join clashes by trying swaps that keep lane cost
        for it in range(20000):
            if not join_clash(sig):
                break
            a, b = rng.sample(range(1, v + 1), 2)
            old = term(a, sig, pi) + term(b, sig, pi), join_clash(sig)
            sig[a], sig[b] = sig[b], sig[a]
            new = term(a, sig, pi) + term(b, sig, pi), join_clash(sig)
            if not (new[0] <= old[0] and new[1] <= old[1]):
                sig[a], sig[b] = sig[b], sig[a]
            else:
                lane += new[0] - old[0]
        key = (lane, join_clash(sig))
        if best is None or key < best[0]:
            best = (key, sig[:], pi[:])
        if key == (0, 0):
            break
    (lane, clash), sig, pi = best
    return {p: sig[p] for p in range(1, v + 1)}, pi, lane, clash


# ---------------------------------------------------------------- positions
def assign_positions(weeks, v):
    """Order each group as [L1, R1, L2] by properly 3-edge-colouring the bipartite
    graph (week, group) -- (bowler, chunk of 3 consecutive appearances), using
    Konig's alternating-path method.  Every bowler then holds each position
    floor/ceil(k/3) times after any prefix of k appearances."""
    seen = {}
    edges = []  # (gnode, bnode, player)
    for wi, w in enumerate(weeks):
        for gi, g in enumerate(w):
            for p in g:
                k = seen.get(p, 0); seen[p] = k + 1
                edges.append((("g", wi, gi), ("b", p, k // 3), p))
    at = {}  # node -> {colour: edge index}
    col = [None] * len(edges)

    def free(node):
        used = at.setdefault(node, {})
        return next(c for c in range(3) if c not in used)

    for ei, (gn, bn, p) in enumerate(edges):
        a, b = free(gn), free(bn)
        if a not in at[bn]:
            c = a
        else:
            # flip the a/b alternating path starting at bn along colour a
            path, node, colour = [], bn, a
            while colour in at.setdefault(node, {}):
                e = at[node][colour]
                path.append(e)
                x, y, _ = edges[e]
                node = y if x == node else x
                colour = b if colour == a else a
            for e in path:
                x, y, _ = edges[e]
                del at[x][col[e]]; del at[y][col[e]]
            for e in path:
                x, y, _ = edges[e]
                col[e] = b if col[e] == a else a
                at[x][col[e]] = e; at[y][col[e]] = e
            c = a
        col[ei] = c
        at[gn][c] = ei; at[bn][c] = ei
    out = [[[None] * 3 for _ in w] for w in weeks]
    for (gn, bn, p), c in zip(edges, col):
        _, wi, gi = gn
        assert out[wi][gi][c] is None
        out[wi][gi][c] = p
    return out


def position_stats(weeks, v):
    cnt = {p: [0, 0, 0] for p in range(1, v + 1)}
    pref = []
    for w in weeks:
        for g in w:
            for pos, p in enumerate(g):
                cnt[p][pos] += 1
        pref.append(max(max(c) - min(c) for c in cnt.values()))
    return cnt, pref


# ---------------------------------------------------------------- driver
PREFIX_NOTE = ("For v = 0 mod 6 with lambda=2 a prefix spread of 2 is unavoidable: "
               "spread<=1 at W=(v-2)/2 forces those weeks to be pair-disjoint, leaving a "
               "perfect matching of unmet pairs that one week (v/3 triples) cannot cover.")


def lane_penalty(weeks, v, players):
    nl = v // 3
    r = len(weeks)
    lo, hi = r // nl, -(-r // nl)
    cnt = lane_cost_counts(weeks, v, [list(range(nl))] * r)
    return sum(max(0, c - hi) + max(0, lo - c) for p in players for c in cnt[p]), cnt


def write(name, data, weeks_flat):
    (OUT / f"{name}.json").write_text(json.dumps(data, indent=1))
    lines = ["[schedule]", "weeks = ["]
    lines += ["  [" + ", ".join(map(str, w)) + "]," for w in weeks_flat]
    lines.append("]")
    (OUT / f"{name}.toml").write_text("\n".join(lines) + "\n")


def summarise(v, weeks, lam, players, pair_players=None):
    """weeks: list of lane-ordered groups (positions already assigned)."""
    pp = pair_players or players
    idx = pair_index(v)
    sub = [i for (a, b), i in idx.items() if a in pp and b in pp]
    cnt = [0] * len(idx)
    spreads = []
    for w in weeks:
        for k in week_pairs(w, idx):
            cnt[k] += 1
        vals = [cnt[i] for i in sub]
        spreads.append(max(vals) - min(vals))
    pen, lc = lane_penalty(weeks, v, players)
    pos_cnt, _ = position_stats(weeks, v)
    pos_pref = []
    pc = {p: [0, 0, 0] for p in range(1, v + 1)}
    for w in weeks:
        for g in w:
            for k, p in enumerate(g):
                pc[p][k] += 1
        pos_pref.append(max(max(pc[p]) - min(pc[p]) for p in players))
    return {
        "players": v, "group": 3,
        "weeks": [[p for g in w for p in g] for w in weeks], "lambda": lam,
        "lane_counts": {str(p): lc[p] for p in range(1, v + 1)},
        "lane_balance_exact": pen == 0, "lane_penalty": pen,
        "prefix_spread": spreads, "worst_prefix_spread": max(spreads),
        "prefix_weeks_with_spread_2": [i + 1 for i, x in enumerate(spreads) if x >= 2],
        "position_order": "[left lane 1st, right lane 1st, left lane 2nd]",
        "position_counts": {str(p): pos_cnt[p] for p in range(1, v + 1)},
        "position_prefix_spread": pos_pref,
    }


def search_designs(v, rng, tries, budget=600):
    """Cyclic designs, each with its best week order; returns list of (key, weeks, classes)."""
    n, m, c, lam = PARAMS[v]
    out, t0 = [], time.time()
    while len(out) < tries and time.time() - t0 < budget:
        classes = find_base_classes(v, rng)
        if classes is None:
            continue
        weeks = develop(v, classes)
        if lam == 1:
            out.append(((0,), weeks, classes))
        else:
            ow, oc = optimise_order(weeks, v, rng, iters=3000 if v > 12 else 6000)
            out.append((oc, ow, classes))
    out.sort(key=lambda t: t[0])
    return out


def lanes_best(weeks, v, rng, z3_s=120):
    w, pen = optimise_lanes(weeks, v, rng)
    status = "sa"
    if pen:
        zw = z3_lanes(weeks, v, timeout_s=z3_s)
        status = "z3 " + getattr(z3_lanes, "last", "?")
        if zw is not None:
            w, pen = zw, 0
    return w, pen, status


def build(v, seed=1):
    rng = random.Random(seed)
    n, m, c, lam = PARAMS[v]
    t0 = time.time()
    allp = list(range(1, v + 1))
    designs = search_designs(v, rng, 40 if lam == 2 else 8)
    cyc_key, cyc_weeks, cyc_classes = designs[0]

    # ---- main single-round file
    sat_file = OUT / f"design_v{v}_sat.json"
    weeks, classes, src = cyc_weeks, cyc_classes, "cyclic"
    if lam == 2:
        weeks, key = optimise_order(weeks, v, rng, iters=40000)
        if sat_file.exists():
            sw = json.loads(sat_file.read_text())
            idx0 = pair_index(v)
            sk = order_cost(range(len(sw)), [week_pairs(w, idx0) for w in sw], len(idx0))
            if sk < key:
                weeks, classes, src = sw, [], "z3"
    lw, lane_pen, lstat = lanes_best(weeks, v, rng)
    if lane_pen and lam == 1:  # week order is free for lambda=1: try other designs
        for _, w2, cl2 in designs[1:]:
            lw2, p2, st2 = lanes_best(w2, v, rng, z3_s=30)
            if p2 < lane_pen:
                lw, lane_pen, lstat, classes = lw2, p2, st2, cl2
            if lane_pen == 0:
                break
    if lane_pen and lam == 2 and src == "cyclic":
        # other base classes whose prefix profile is as good may lane-balance exactly
        for k2, w2, cl2 in designs[1:12]:
            w2, k2 = optimise_order(w2, v, rng, iters=20000)
            if k2[:2] > key[:2]:
                continue
            lw2, p2, st2 = lanes_best(w2, v, rng, z3_s=20)
            if p2 < lane_pen:
                lw, lane_pen, lstat, classes, key = lw2, p2, st2, cl2, k2
            if lane_pen == 0:
                break
    weeks = lw
    sigma, lane_pi, lane2_pen, clash = second_cycle(weeks, v, rng)
    weeks_pos = assign_positions(weeks, v)
    kind = "Kirkman triple system" if lam == 1 else "resolvable 2-(v,3,2) design"
    if src == "z3":
        how = ("found directly by z3 (prefix_sat.py) with weeks 1-4 pair-disjoint and all "
               "couples met by week 7; z3 proved weeks 1-4 disjoint + all met by week 6 "
               "unsatisfiable, so 2 spread-2 prefixes is optimal for v=12")
    else:
        how = (f"points Z_{n}x{{0..{m-1}}}+inf, {c} base class(es) found by randomised "
               f"backtracking on difference counts, developed mod {n}"
               + (f"; best of {len(designs)} base classes for prefix profile" if lam == 2 else ""))
    data = summarise(v, weeks_pos, lam, allp)
    data["method"] = (f"{kind}: {how}; lane order by simulated annealing, then z3 "
                      f"({lstat}); week order by annealing on prefix spread; positions by "
                      f"Konig 3-edge-colouring of (group)-(bowler, 3-appearance chunk) graph")
    if lane_pen:
        data["lane_note"] = (f"best found leaves {lane_pen} player-lane cell(s) off by one; "
                             f"exact assignment for this design: {lstat}")
    if v == 15:
        data["lane_note"] = ("exact lane balance looks impossible for v=15: z3 proves it "
                             "unsatisfiable in milliseconds for every KTS(15) tried (40 distinct "
                             "z3-generated resolutions plus the cyclic ones); best = 1 cell off")
    if lam == 2:
        data["prefix_note"] = PREFIX_NOTE
    data["base_classes"] = [[[("inf" if x == -1 else list(x)) for x in b] for b in cl]
                            for cl in classes]
    data["second_cycle"] = {
        "rule": "Cycle 2 replays cycle 1's weeks with player p replaced by relabel[p] and the "
                "group on lane pair l (0-based) moved to lane pair lane_map[l]. Pair counts "
                "restart from a uniform lambda, so cycle-2 prefix spreads equal cycle 1's. "
                "See v{N}_x2.json for a ready-made double round (lanes and positions tuned).",
        "lane_map": lane_pi,
        "relabel": {str(k): x for k, x in sigma.items()},
        "two_cycle_lane_penalty": lane2_pen,
        "join_repeated_groups": clash,
    }
    write(f"v{v}", data, data["weeks"])
    print(f"v={v} main: r={len(weeks)} lane_pen={lane_pen} ({lstat}) "
          f"bad={data['prefix_weeks_with_spread_2']} pos_pref={max(data['position_prefix_spread'])}")

    # ---- x2: two cycles
    nl = v // 3
    cyc2 = []
    for w in weeks:
        nw = [None] * nl
        for l, g in enumerate(w):
            nw[lane_pi[l]] = [sigma[p] for p in g]
        cyc2.append(nw)
    both, pen2 = optimise_lanes(weeks + cyc2, v, rng, frozen=len(weeks), restarts=3)
    x2stat = "sa"
    if pen2:
        zb = z3_lanes(both, v, timeout_s=180, frozen=len(weeks))
        x2stat = "z3 " + z3_lanes.last
        if zb is not None:
            both, pen2 = zb, 0
    both_pos = assign_positions(both, v)
    d2 = summarise(v, both_pos, lam, allp)
    d2["cycles"] = 2
    d2["method"] = (f"two rounds: cycle 1 = v{v}.json weeks/lanes; cycle 2 = same design "
                    f"under a player relabelling and lane-pair map chosen by annealing against "
                    f"cycle 1's lane counts, then cycle-2 lane order re-solved with cycle 1 "
                    f"frozen ({x2stat}); positions re-coloured over both rounds")
    d2["join_repeated_groups"] = len({tuple(sorted(g)) for g in weeks[-1]}
                                     & {tuple(sorted(g)) for g in both[len(weeks)]})
    if pen2:
        d2["lane_note"] = (f"best found leaves {pen2} bowler-lane cell(s) outside "
                           f"floor/ceil(2r/n) while keeping cycle 1 exact; z3 (8 min, three "
                           f"relabellings) returned unknown")
    write(f"v{v}_x2", d2, d2["weeks"])
    print(f"v={v} x2: lane_pen={pen2} join_clash={d2['join_repeated_groups']} "
          f"worst={d2['worst_prefix_spread']}")

    # ---- vacant: 1-rotational design, base block j on lane pair j, inf = vacancy
    real = list(range(1, v))
    if lam == 2:
        vcls = cyc_classes
        vw = develop(v, vcls)
        vbase = [[("inf" if x == -1 else x[1]) for x in b] for b in vcls[0]]
        vgroup = f"Z_{v-1}"
    else:
        res = one_rotational_kts(v, rng, budget=60)
        if res is not None:
            vw, base = develop_1rot(v, res[1])
            vbase = [["inf" if z == -1 else z for z in b] for b in base]
            vgroup = (f"1-rotational KTS over Z_{v-1} + inf (base class fixed by "
                      f"+{(v-1)//2}, weeks s=0..{(v-3)//2})")
        else:
            vw = [list(w) for w in lw]
            vbase = data["base_classes"]
            vgroup = (f"no 1-rotational KTS({v}) under Z_{v-1} exists (exhaustive search); "
                      f"uses the v{v}.json KTS, Z_{n}x{{0..{m-1}}} + inf, with inf = vacancy")
        vw, vpen = optimise_lanes(vw, v, rng, players=real)
    if lam == 2:
        vpen, _ = lane_penalty(vw, v, real)
    if lam == 2:  # reorder weeks for prefix balance (lanes untouched)
        vw, _ = optimise_order(vw, v, rng, iters=20000)
    vpos = assign_positions(vw, v)
    dv = summarise(v, vpos, lam, real)
    dv["vacant"] = v
    inf_lanes = sorted({l for w in vw for l, g in enumerate(w) if v in g})
    dv["base_class"] = vbase
    if lam == 2:
        dv["method"] = (f"1-rotational {kind} over Z_{v-1} + inf, inf = vacancy (player {v}); "
                        f"base block j kept on lane pair j in every developed week, so each "
                        f"real bowler meets each base point once and lands on each lane pair "
                        f"floor/ceil(r/n) times; the short group is always on lane pair(s) "
                        f"{[l + 1 for l in inf_lanes]}; week order annealed for prefix spread; "
                        f"positions coloured with the vacancy treated as a player")
    else:
        dv["method"] = (f"{vgroup}; vacancy = player {v}; lane order by simulated annealing "
                        f"on the real bowlers only (fixed base-block lanes do not balance a "
                        f"KTS, which is developed over only half the group); positions "
                        f"coloured with the vacancy treated as a player")
    dv["finite_lane_balance_exact"] = vpen == 0
    dv["note"] = ("lane_counts, positions, lambda and prefix spreads are judged on the "
                  f"{v-1} real bowlers; player {v} is the empty slot")
    if lam == 2:
        dv["prefix_note"] = PREFIX_NOTE
    write(f"v{v}_vacant", dv, dv["weeks"])
    print(f"v={v} vacant: finite lane_pen={vpen} inf lanes={inf_lanes} "
          f"bad={dv['prefix_weeks_with_spread_2']} ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    vs = [int(x) for x in sys.argv[1:]] or [12, 15, 18, 21, 24, 27]
    for v in vs:
        build(v)
