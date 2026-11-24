"""Re-resolve part of a uniform design (exact cover, Knuth's Algorithm X).

Given some parallel classes of a design (their union is a regular graph G on the points),
find new parallel classes with the given block sizes whose blocks are cliques of G and
cover every edge of G exactly once.  Examples (v = 24):
  2 four-way classes  -> 3 three-way classes   (0-1-7 -> 0-4-5)
  3 three-way classes -> 2 four-way classes    (0-10-1 -> 0-7-3)
  1 three-way + j four-way -> 2 two-way + j four-way  (towards 2-0-7)
Also the generic helpers used by the case drivers (load a file's weeks, split moves)."""
import itertools, json, os, random, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
HYB = os.path.dirname(os.path.dirname(HERE))

def load_weeks(fname):
    d = json.load(open(os.path.join(HYB, 'files', fname)))
    out = []
    for wk in d['weeks']:
        gs = []
        for e in wk:
            if e is None: continue
            gs += e['wrapped'] if isinstance(e, dict) else [e]
        out.append([list(g) for g in gs])
    return d['players'], out

class Timeout(Exception): pass

def solve_x(X, Y, limit_nodes=None, deadline=None, rng=None):
    """X: col -> set(rows), Y: row -> list(cols).  Yields one solution (list of rows) or None."""
    sol = []; nodes = [0]
    def select(r):
        cols = []
        for j in Y[r]:
            for i in X[j]:
                for k in Y[i]:
                    if k != j: X[k].discard(i)
            cols.append(X.pop(j))
        return cols
    def deselect(r, cols):
        for j in reversed(Y[r]):
            X[j] = cols.pop()
            for i in X[j]:
                for k in Y[i]:
                    if k != j: X[k].add(i)
    def rec():
        if not X: return True
        nodes[0] += 1
        if (limit_nodes and nodes[0] > limit_nodes) or (deadline and (nodes[0] & 1023) == 0 and time.time() > deadline):
            raise Timeout
        c = min(X, key=lambda c: len(X[c]))
        rows = list(X[c])
        if rng: rng.shuffle(rows)
        else: rows.sort()
        for r in rows:
            sol.append(r); cols = select(r)
            if rec(): return True
            deselect(r, cols); sol.pop()
        return False
    try:
        ok = rec()
    except Timeout:
        return 'timeout', nodes[0]
    return (list(sol) if ok else None), nodes[0]

def cliques(adj, k, pts):
    out = []
    def ext(cl, cand):
        if len(cl) == k: out.append(tuple(cl)); return
        for i, q in enumerate(cand):
            ext(cl + [q], [r for r in cand[i + 1:] if r in adj[q]])
    for p in pts:
        ext([p], sorted(q for q in adj[p] if q > p))
    return out

def regroup(points, edges, sizes, limit_nodes=None, timeout=None, seed=None):
    """points: iterable; edges: set of frozensets; sizes: list of block sizes, one per new class.
    Returns list of classes (lists of tuples) or None (proved impossible) or 'timeout'."""
    pts = sorted(points)
    adj = {p: set() for p in pts}
    for e in edges:
        a, b = tuple(e); adj[a].add(b); adj[b].add(a)
    cl = {k: cliques(adj, k, pts) for k in set(sizes)}
    X = {}; Y = {}
    for e in edges: X[('e',) + tuple(sorted(e))] = set()
    for c in range(len(sizes)):
        for p in pts: X[('p', p, c)] = set()
    # symmetry: among classes of equal size, the block of pts[0] has increasing 2nd point
    p0 = pts[0]
    for c, k in enumerate(sizes):
        prev = [d for d in range(c) if sizes[d] == k]
        nxt = [d for d in range(c + 1, len(sizes)) if sizes[d] == k]
        for B in cl[k]:
            if B[0] == p0:
                # B[1] is the 2nd point; class order c within same-size group -> rank
                rank = len(prev); others = len(nxt)
                nb = sorted(adj[p0])
                pos = nb.index(B[1])
                if pos < rank or pos > len(nb) - 1 - others * (k - 1): continue
            r = (c, B)
            Y[r] = [('e',) + pr for pr in itertools.combinations(B, 2)] + [('p', p, c) for p in B]
            for j in Y[r]: X[j].add(r)
    deadline = time.time() + timeout if timeout else None
    rng = random.Random(seed) if seed is not None else None
    sol, nodes = solve_x(X, Y, limit_nodes, deadline, rng)
    if sol is None or sol == 'timeout': return sol
    out = [[] for _ in sizes]
    for c, B in sol: out[c].append(list(B))
    return out

def class_edges(classes):
    E = set()
    for wk in classes:
        for g in wk:
            for a, b in itertools.combinations(g, 2): E.add(frozenset((a, b)))
    return E

def convert(weeks, idx, sizes, **kw):
    """Replace weeks[idx] by new classes with block sizes `sizes` (if possible)."""
    pts = sorted(p for g in weeks[0] for p in g)
    E = class_edges([weeks[i] for i in idx])
    r = regroup(pts, E, sizes, **kw)
    if r is None or r == 'timeout': return r
    return [wk for i, wk in enumerate(weeks) if i not in idx] + r

def split4(wk):
    """K4 class -> three matchings."""
    return [[m for g in wk for m in ([g[a], g[b]], [g[c], g[d]])] for a, b, c, d in ((0, 1, 2, 3), (0, 2, 1, 3), (0, 3, 1, 2))]

def mix(weeks):
    return tuple(sum(1 for wk in weeks if len(wk[0]) == k) for k in (2, 3, 4))
