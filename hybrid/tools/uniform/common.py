"""Shared finishing steps for uniform hybrids: lane assignment (annealing), positions
(de Werra, tools/positions.py), JSON writer in hybrid/verify.py format."""
import json, math, os, random, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
HYB = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HYB), 'tools'))
sys.path.insert(0, HYB)
from positions import assign          # noqa: E402

def lanes_needed(weeks):
    n = 0
    for wk in weeks:
        k = len(wk[0]); n = max(n, -(-len(wk) // 2) if k == 2 else len(wk))
    return n

def check_design(v, weeks):
    meet = collections.Counter()
    for wk in weeks:
        assert sorted(p for g in wk for p in g) == list(range(1, v + 1)), "not a partition"
        assert len({len(g) for g in wk}) == 1, "week not uniform"
        for g in wk:
            for i in range(len(g)):
                for j in range(i + 1, len(g)):
                    meet[frozenset((g[i], g[j]))] += 1
    bad = sum(1 for a in range(1, v + 1) for b in range(a + 1, v + 1) if meet[frozenset((a, b))] != 1)
    assert bad == 0, f"{bad} couples not exactly once"

def anneal_lanes(v, weeks, n, seed=0, iters=400000, restarts=20, W=3):
    """Returns (slots, caps): slots[w] = list of n*cap entries (group index or -1).
    Cost = sum over bowlers of (lane deviation + W if any deviation), so that when
    exactness is impossible the deviation is concentrated on few bowlers."""
    R = len(weeks); lo, hi = R // n, -(-R // n)
    caps = [2 if (len(wk[0]) == 2 and len(wk) > n) else 1 for wk in weeks]
    pen = lambda c: (c - hi if c > hi else (lo - c if c < lo else 0))
    bp = lambda d: d + W * (d > 0)
    best_all = None
    rng = random.Random(seed)
    for rs in range(restarts):
        slots = []
        for w, wk in enumerate(weeks):
            s = list(range(len(wk))) + [-1] * (n * caps[w] - len(wk)); rng.shuffle(s); slots.append(s)
        cnt = [[0] * n for _ in range(v + 1)]
        for w, wk in enumerate(weeks):
            for si, g in enumerate(slots[w]):
                if g >= 0:
                    for p in wk[g]: cnt[p][si // caps[w]] += 1
        dev = [sum(pen(c) for c in cnt[p]) for p in range(v + 1)]
        cost = sum(bp(dev[p]) for p in range(1, v + 1))
        T = 1.0; best = cost; bestslots = [s[:] for s in slots]
        for it in range(iters):
            if best == 0: break
            w = rng.randrange(R); c = caps[w]; S = slots[w]
            a = rng.randrange(len(S)); b = rng.randrange(len(S))
            La, Lb = a // c, b // c
            if La == Lb or (S[a] < 0 and S[b] < 0): continue
            ga = weeks[w][S[a]] if S[a] >= 0 else (); gb = weeks[w][S[b]] if S[b] >= 0 else ()
            d = 0; nd = []
            for p, X, Y in [(p, La, Lb) for p in ga] + [(p, Lb, La) for p in gb]:
                dd = dev[p] + pen(cnt[p][X] - 1) - pen(cnt[p][X]) + pen(cnt[p][Y] + 1) - pen(cnt[p][Y])
                d += bp(dd) - bp(dev[p]); nd.append((p, X, Y, dd))
            if d <= 0 or rng.random() < math.exp(-d / T):
                for p, X, Y, dd in nd: cnt[p][X] -= 1; cnt[p][Y] += 1; dev[p] = dd
                S[a], S[b] = S[b], S[a]; cost += d
                if cost < best: best = cost; bestslots = [s[:] for s in slots]
            T = max(0.05, T * 0.99997)
        if best_all is None or best < best_all[0]: best_all = (best, bestslots)
        if best == 0: break
    return best_all[1], caps

def lane_off(v, weeks, n, slots, caps):
    R = len(weeks); lo, hi = R // n, -(-R // n); cnt = collections.Counter()
    for w, wk in enumerate(weeks):
        for si, g in enumerate(slots[w]):
            if g >= 0:
                for p in wk[g]: cnt[(p, si // caps[w])] += 1
    return sum(1 for p in range(1, v + 1) if any(not lo <= cnt[(p, L)] <= hi for L in range(n)))

def best_lanes(v, variants, n=None, tries=4, **kw):
    """variants: list of candidate designs (same mix).  Returns (weeks, slots, caps, off)."""
    best = None
    for i, W in enumerate(variants):
        nn = n or lanes_needed(W)
        for t in range(tries):
            sl, cp = anneal_lanes(v, W, nn, seed=1000 * i + t, **kw)
            off = lane_off(v, W, nn, sl, cp)
            if best is None or off < best[3]: best = (W, sl, cp, off)
            if off == 0: return best
    return best

def build(v, weeks, method, fname, n=None, seed=0, extra=None, lanes=None, **kw):
    """weeks: 1-based groups.  Lane-anneal (or use lanes=(slots,caps)), assign positions,
    write hybrid/files/fname."""
    check_design(v, weeks)
    n = n or lanes_needed(weeks)
    slots, caps = lanes or anneal_lanes(v, weeks, n, seed=seed, **kw)
    # positions per format, groups taken in week order
    byk = collections.defaultdict(list)
    for w, wk in enumerate(weeks): byk[len(wk[0])].append(w)
    ordered = [None] * len(weeks)
    for k, ws in byk.items():
        out = assign([weeks[w] for w in ws], k)
        for w, wk in zip(ws, out): ordered[w] = wk
    W = []
    for w, wk in enumerate(ordered):
        c = caps[w]; row = []
        for L in range(n):
            gs = [wk[g] for g in slots[w][L * c:(L + 1) * c] if g >= 0]
            row.append(None if not gs else (gs[0] if len(gs) == 1 else {"wrapped": gs}))
        W.append(row)
    d = {"players": v, "lane_pairs": n, "weeks": W, "method": method}
    if extra: d.update(extra)
    path = os.path.join(HYB, 'files', fname)
    with open(path, 'w') as f:
        f.write(json.dumps({k: x for k, x in d.items() if k != 'weeks'})[:-1] + ',\n "weeks": [\n  '
                + ',\n  '.join(json.dumps(wk, separators=(',', ':')) for wk in W) + '\n ]}\n')
    import verify
    r = verify.check(path)
    print(json.dumps({k: r[k] for k in ('file', 'weeks', 'lane_pairs', 'valid', 'format_fair', 'mix_2_3_4', 'lane_off_bowlers', 'position_off')}))
    return r

def clanes(v, weeks, n=None, seconds=30, procs=4, W=3, seed=0, rit=3000000):
    """C annealer (lanes.c), `procs` seeds in parallel; returns (slots, caps, off)."""
    import subprocess
    n = n or lanes_needed(weeks); R = len(weeks)
    caps = [2 if (len(wk[0]) == 2 and len(wk) > n) else 1 for wk in weeks]
    spec = f"{v} {n} {R} {W}\n" + "\n".join(f"{caps[w]} {len(wk)} {len(wk[0])} " + " ".join(str(p) for g in wk for p in g) for w, wk in enumerate(weeks)) + "\n"
    ps = [subprocess.Popen([os.path.join(HERE, 'lanes'), str(seed + i), str(seconds), str(rit)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True) for i in range(procs)]
    for p in ps: p.stdin.write(spec); p.stdin.close()
    import time as _t
    best = None; left = list(ps)
    while left:
        for p in list(left):
            if p.poll() is None: continue
            left.remove(p)
            L = p.stdout.read().split('\n'); off, cost = map(int, L[0].split())
            slots = [list(map(int, L[1 + w].split())) for w in range(R)]
            if best is None or (off, cost) < best[2:]: best = (slots, caps, off, cost)
        if best is not None and best[3] == 0:
            for p in left: p.kill(); p.wait()
            break
        _t.sleep(0.2)
    return best[0], best[1], best[2]

def finish(v, weeks, fname, method, seconds=30, procs=4, n=None, W=3, keep_better=True):
    """Lane-anneal with lanes.c, assign positions, write the file (only if it is new or has
    fewer lane-off bowlers than the existing uniform file)."""
    check_design(v, weeks)
    weeks = sorted(weeks, key=lambda wk: -len(wk[0]))
    n = n or lanes_needed(weeks)
    slots, caps, off = clanes(v, weeks, n, seconds=seconds, procs=procs, W=W)
    path = os.path.join(HYB, 'files', fname)
    if keep_better and os.path.exists(path):
        import verify
        old = verify.check(path)['lane_off_bowlers']
        if old <= off:
            print(fname, f'not written: existing file has {old} off, new {off}'); return None
    return build(v, weeks, method + '; lane pairs by simulated annealing (lanes.c), positions by de Werra colouring (tools/positions.py)', fname, n=n, lanes=(slots, caps))
