"""Equitable position assignment within groups (de Werra).

weeks: list of weeks, each a list of groups (lists of players), group size k.
Returns the same weeks with each group reordered so every player holds each
position floor(r/k) or ceil(r/k) times -- and, because each player's weeks are
split into consecutive chunks of k, every prefix is within about one too.
Method: split each player's appearances (in week order) into chunks of k ->
vertices of degree <= k; properly k-edge-colour the bipartite graph
(group-instances x chunks) by Konig's alternating paths; colour = position."""
from collections import defaultdict

def assign(weeks, k):
    seen = defaultdict(int)
    edges = []                                   # (left=(w,g), right=(p,chunk))
    for w, wk in enumerate(weeks):
        for g, grp in enumerate(wk):
            for p in grp:
                edges.append(((w, g), (p, seen[p] // k), p)); seen[p] += 1
    colL = defaultdict(dict); colR = defaultdict(dict)   # vertex -> colour -> edge idx
    colour = {}
    def free(side, v):
        return next(c for c in range(k) if c not in side[v])
    for e, (u, v, p) in enumerate(edges):
        a = free(colL, u); b = free(colR, v)
        if a not in colR[v]:
            c = a
        elif b not in colL[u]:
            c = b
        else:
            # alternating a/b path from v, starting with colour a; swap it
            path, x, side, cur = [], v, "R", a
            while True:
                tbl = colR if side == "R" else colL
                if cur not in tbl[x]: break
                f = tbl[x][cur]; path.append(f)
                fu, fv, _ = edges[f]
                x = fu if side == "R" else fv
                side = "L" if side == "R" else "R"
                cur = b if cur == a else a
            for f in path:
                fu, fv, _ = edges[f]; old = colour[f]
                del colL[fu][old]; del colR[fv][old]
            for f in path:
                fu, fv, _ = edges[f]; new = b if colour[f] == a else a
                colour[f] = new; colL[fu][new] = f; colR[fv][new] = f
            c = a
        colour[e] = c; colL[u][c] = e; colR[v][c] = e
    out = [[[None] * len(grp) for grp in wk] for wk in weeks]
    for e, ((w, g), _, p) in enumerate(edges):
        out[w][g][colour[e]] = p
    return out
