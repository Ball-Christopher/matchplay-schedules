#!/usr/bin/env python3
"""Position-within-group balance by equitable bipartite edge-colouring (de Werra).

Positions per group of 4: [left lane 1st, right lane 1st, left lane 2nd, right lane 2nd].
Left vertices: (week, group).  Right vertices: (bowler, chunk) where a bowler's
appearances, in week order, are cut into chunks of k (k = group size).  Each edge
(week, group)-(bowler, chunk) gets a colour 0..k-1 by Konig's alternating-path
method; colour = position.  Every chunk of k consecutive weeks therefore holds each
position once, so over any prefix a bowler's position counts differ by at most 1,
and over r weeks each count is floor(r/k) or ceil(r/k).
Lane order and group membership are untouched.

Usage as a library:  assign_positions(weeks) -> weeks with each chunk reordered.
`weeks` may be a list of flat permutations (chunks of k read in order) or a list of
lists of groups.  CLI:  python3 positions.py in.json [out.json] (key "weeks").
"""
import json, sys

def _as_groups(weeks, k):
    if weeks and isinstance(weeks[0][0], int):
        return [[list(w[i:i + k]) for i in range(0, len(w), k)] for w in weeks], True
    return [[list(g) for g in w] for w in weeks], False

def assign_positions(weeks, k=4):
    groups, flat = _as_groups(weeks, k)
    seen = {}
    edges = []  # (left_id, right_id, bowler)
    left = {}
    for w, wk in enumerate(groups):
        for g, G in enumerate(wk):
            assert len(G) == k
            lid = left.setdefault((w, g), len(left))
            for p in G:
                c = seen.get(p, 0); seen[p] = c + 1
                edges.append((lid, ("R", p, c // k), p))
    # colour maps: at[vertex][colour] = edge index
    at = {}
    col = [None] * len(edges)
    def free(vx):
        d = at.setdefault(vx, {})
        for c in range(k):
            if c not in d:
                return c
        raise RuntimeError("degree > k")
    for e, (u, vR, _) in enumerate(edges):
        U, V = ("L", u), vR
        a, b = free(U), free(V)
        if a not in at[V]:
            c = a
        else:
            # flip the a/b alternating path starting at V (it cannot reach U)
            path = []
            x, want = V, a
            while want in at.get(x, {}):
                f = at[x][want]
                path.append(f)
                fu, fv, _ = edges[f]
                x = ("L", fu) if x == fv else fv
                want = b if want == a else a
            for f in path:  # remove then re-add swapped
                fu, fv, _ = edges[f]
                for y in (("L", fu), fv):
                    del at[y][col[f]]
            for f in path:
                col[f] = b if col[f] == a else a
                fu, fv, _ = edges[f]
                for y in (("L", fu), fv):
                    assert col[f] not in at[y]
                    at[y][col[f]] = f
            c = a
        col[e] = c
        at[U][c] = e; at[V][c] = e
    out = [[[None] * k for _ in wk] for wk in groups]
    inv = {lid: wg for wg, lid in left.items()}
    for e, (u, _, p) in enumerate(edges):
        w, g = inv[u]
        out[w][g][col[e]] = p
    if flat:
        return [[p for G in wk for p in G] for wk in out]
    return out

def position_counts(weeks, k=4):
    groups, _ = _as_groups(weeks, k)
    cnt = {}
    for wk in groups:
        for G in wk:
            for i, p in enumerate(G):
                cnt.setdefault(p, [0] * k)[i] += 1
    return cnt

def prefix_position_spread(weeks, k=4):
    """Per prefix W: max over bowlers of (max - min) position count."""
    groups, _ = _as_groups(weeks, k)
    cnt = {}; out = []
    for wk in groups:
        for G in wk:
            for i, p in enumerate(G):
                cnt.setdefault(p, [0] * k)[i] += 1
        out.append(max(max(c) - min(c) for c in cnt.values()))
    return out

if __name__ == "__main__":
    d = json.load(open(sys.argv[1]))
    d["weeks"] = assign_positions(d["weeks"], d.get("group", 4))
    d["position_counts"] = {str(p): c for p, c in sorted(position_counts(d["weeks"], d.get("group", 4)).items())}
    json.dump(d, open(sys.argv[2] if len(sys.argv) > 2 else sys.argv[1], "w"))
    print("prefix position spread:", prefix_position_spread(d["weeks"], d.get("group", 4)))
