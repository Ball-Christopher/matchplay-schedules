"""Cyclic base-class search for uniformly resolvable designs.

Points: Z_m x {0..rows-1} (index i*m+x) plus fixed points inf_0..inf_{f-1} (index rows*m+j).
The group Z_m acts on x and fixes the inf points.  We search one *base parallel class*
per entry of `base_ks` (its block size); each base class is developed mod m into m weeks.
`fixed_weeks` are invariant weeks given explicitly (e.g. the group/"leave" class).
Every couple must meet exactly once, i.e. every pair-orbit not covered by a fixed week
is covered exactly once by the base classes:
  pure  ('p', i, d)       d = +-difference in row i (d != m/2 unless forbidden by a fixed week)
  mixed ('m', i, j, d)    rows i<j, d = y - x
  inf   ('i', j, i)       inf_j with row i: inf_j's finite partners over all base classes
                          must hit every row exactly once.
Randomised backtracking with restarts.  Returns the full list of weeks (lists of groups)."""
import itertools, random, sys, time

def key(a, b, m, rows):
    F = rows * m
    if a >= F and b >= F: return ('ii', min(a, b), max(a, b))
    if a >= F: a, b = b, a
    if b >= F: return ('i', b - F, a // m)
    i, x = divmod(a, m); j, y = divmod(b, m)
    if i == j:
        d = (y - x) % m; return ('p', i, min(d, m - d))
    if i > j: i, j, x, y = j, i, y, x
    return ('m', i, j, (y - x) % m)

def develop(block, t, m, rows):
    F = rows * m
    return [p if p >= F else (p // m) * m + (p % m + t) % m for p in block]

def search(m, rows, f, base_ks, fixed_weeks=(), seed=0, node_limit=200000, time_limit=60):
    F = rows * m; V = F + f
    rng = random.Random(seed)
    # pair-orbits used by fixed weeks
    forb = set()
    for wk in fixed_weeks:
        for g in wk:
            for a, b in itertools.combinations(g, 2): forb.add(key(a, b, m, rows))
    t0 = time.time()
    while time.time() - t0 < time_limit:
        used = set(forb); classes = []; nodes = [0]
        def rec_class(c):
            if c == len(base_ks): return True
            k = base_ks[c]; free = list(range(V)); blocks = []
            return rec_block(c, k, set(free), blocks)
        def rec_block(c, k, free, blocks):
            if not free:
                classes.append([list(b) for b in blocks])
                if rec_class(c + 1): return True
                classes.pop(); return False
            nodes[0] += 1
            if nodes[0] > node_limit: return False
            p = min(free); rest = [q for q in free if q != p]
            cand = [q for q in rest if key(p, q, m, rows) not in used]
            rng.shuffle(cand)
            def ext(blk, keys, start):
                if len(blk) == k:
                    yield blk, keys; return
                for idx in range(start, len(cand)):
                    q = cand[idx]; nk = []
                    ok = True
                    for b in blk:
                        kk = key(b, q, m, rows)
                        if kk in used or kk in keys or kk in nk or kk[0] == 'ii': ok = False; break
                        if kk[0] == 'p' and m % 2 == 0 and kk[2] == m // 2: ok = False; break
                        nk.append(kk)
                    if ok:
                        yield from ext(blk + [q], keys + nk, idx + 1)
            for blk, keys in ext([p], [], 0):
                for kk in keys: used.add(kk)
                blocks.append(blk)
                if rec_block(c, k, free - set(blk), blocks): return True
                blocks.pop()
                for kk in keys: used.discard(kk)
                if nodes[0] > node_limit: return False
            return False
        if rec_class(0):
            weeks = [list(map(list, w)) for w in fixed_weeks]
            for cl in classes:
                for t in range(m):
                    weeks.append([develop(b, t, m, rows) for b in cl])
            return weeks
        seed += 1
    return None

def to_one_based(weeks):
    return [[[p + 1 for p in g] for g in wk] for wk in weeks]

def search_c(m, rows, f, base_ks, fixed_weeks=(), seed=0, node_limit=2000000, time_limit=60):
    """Same search via the C core (basecls.c)."""
    import subprocess
    F = rows * m; V = F + f
    ids = {}; tab = []
    for a in range(V):
        row = []
        for b in range(V):
            if a == b: row.append(-1); continue
            kk = key(a, b, m, rows)
            if kk[0] == 'ii' or (kk[0] == 'p' and m % 2 == 0 and kk[2] == m // 2): row.append(-1); continue
            row.append(ids.setdefault(kk, len(ids)))
        tab.append(row)
    usedk = set()
    for wk in fixed_weeks:
        for g in wk:
            for a, b in itertools.combinations(g, 2):
                kk = key(a, b, m, rows)
                if kk in ids: usedk.add(ids[kk])
    spec = f"{V} {len(ids)} {len(base_ks)} {' '.join(map(str, base_ks))}\n" + '\n'.join(' '.join(map(str, r)) for r in tab) + f"\n{len(usedk)} {' '.join(map(str, usedk))}\n"
    exe = __file__.rsplit('/', 1)[0] + '/basecls'
    p = subprocess.run([exe, str(seed), str(time_limit), str(node_limit)], input=spec, capture_output=True, text=True)
    if p.returncode != 0: return None
    classes = [[] for _ in base_ks]
    for line in p.stdout.split('\n'):
        if line.strip():
            xs = list(map(int, line.split())); classes[xs[0]].append(xs[1:])
    weeks = [list(map(list, w)) for w in fixed_weeks]
    for cl in classes:
        for t in range(m):
            weeks.append([develop(b, t, m, rows) for b in cl])
    return weeks
