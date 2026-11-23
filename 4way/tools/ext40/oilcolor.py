"""Fewest contiguous clash-free blocks for a fixed set of weeks = chromatic number of the
graph on weeks (edge = two weeks share a couple); exact DSATUR-style backtracking."""
import sys, json, itertools
def clash_graph(W):
    P = [set(frozenset(p) for g in wk for p in itertools.combinations(g, 2)) for wk in W]
    n = len(W); return [[i != j and bool(P[i] & P[j]) for j in range(n)] for i in range(n)]
def colour(adj, kmax, limit=2_000_000):
    n = len(adj); col = [-1] * n; cnt = [0]
    def pick():
        best = None
        for v in range(n):
            if col[v] >= 0: continue
            sat = len({col[u] for u in range(n) if adj[v][u] and col[u] >= 0})
            deg = sum(adj[v]); key = (sat, deg)
            if best is None or key > best[0]: best = (key, v)
        return best[1] if best else None
    def rec(used):
        cnt[0] += 1
        if cnt[0] > limit: return None
        v = pick()
        if v is None: return True
        forb = {col[u] for u in range(n) if adj[v][u] and col[u] >= 0}
        for c in range(min(used + 1, kmax)):
            if c in forb: continue
            col[v] = c
            r = rec(max(used, c + 1))
            if r: return True
            if r is None: col[v] = -1; return None
            col[v] = -1
        return False
    r = rec(0); return (list(col) if r else None), r
if __name__ == "__main__":
    W = json.load(open(sys.argv[1]))["weeks"]; adj = clash_graph(W)
    for k in range(4, 20):
        c, r = colour(adj, k)
        print(k, r, flush=True)
        if r: print(json.dumps(c)); break
