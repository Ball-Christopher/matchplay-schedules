"""Spec generator for sa.c: points Z_m x ncls (id m*c+i) plus nfix fixed points (ids m*ncls+j).
Pair types = orbits of pairs under i -> i+1."""
import itertools, sys
LAM = 3

class Sys:
    def __init__(s, m, ncls=4, nfix=0):
        s.m, s.ncls, s.nfix = m, ncls, nfix; s.n = m * ncls + nfix
        s.type = [[-1] * s.n for _ in range(s.n)]; s.osize = []; s.rep = []
        for p in range(s.n):
            for q in range(p + 1, s.n):
                if s.type[p][q] >= 0: continue
                t = len(s.osize); orb = set()
                for k in range(m):
                    a, b = s.sh(p, k), s.sh(q, k); orb.add((min(a, b), max(a, b)))
                    s.type[a][b] = s.type[b][a] = t
                s.osize.append(len(orb)); s.rep.append((p, q))
        s.nt = len(s.osize)
        for p in range(s.n): s.type[p][p] = 0
    def sh(s, p, k):
        if p >= s.m * s.ncls: return p
        return s.m * (p // s.m) + (p % s.m + k) % s.m
    def pt(s, c, i): return s.m * c + i % s.m
    def tperm(s, phi):
        """induced action of a point permutation (commuting with/normalising Z_m) on types"""
        return [s.type[phi[p]][phi[q]] for (p, q) in s.rep]
    def wtypes(s, week):
        """types covered by a Z_m-invariant week (each once per pair of the orbit)"""
        c = {}
        for g in week:
            for a, b in itertools.combinations(g, 2): c[s.type[a][b]] = c.get(s.type[a][b], 0) + 1
        out = []
        for t, x in c.items():
            assert x % s.osize[t] == 0; out += [t] * (x // s.osize[t])
        return out
    def transversal(s, off):
        wk = [[s.pt(c, off[c] + k) for c in range(s.ncls)] for k in range(s.m)]
        if s.nfix: wk.append(list(range(s.m * s.ncls, s.n)))
        return wk
    def spec(s, phi, nb, tie, inv, invblock, path=None, oil=True, extra=()):
        """inv: list of weeks; invblock[i] = base block index k the week joins, or -1 (own block).
        Returns None if infeasible on counts."""
        invc = [0] * s.nt; forb = [[0] * s.nt for _ in range(nb)]
        for wk, k in zip(inv, invblock):
            for t in s.wtypes(wk):
                invc[t] += 1
                if k >= 0: forb[k][t] += 1
        for wk in extra:   # explicit extra base weeks (developed mod m, own block): one pair = one cover of its type
            for g in wk:
                for a, b in itertools.combinations(g, 2): invc[s.type[a][b]] += 1
        target = []; wt = []
        for t in range(s.nt):
            if s.osize[t] == s.m: target.append(LAM - invc[t]); wt.append(1)
            else:
                if invc[t] != LAM: return None
                target.append(0); wt.append(10)
        if min(target) < 0: return None
        if oil and any(x > 1 for f in forb for x in f): return None
        if path:
            with open(path, "w") as f:
                f.write(f"{s.n} {nb} {int(tie) if tie is not True else nb} {s.nt}\n" + " ".join(map(str, phi)) + "\n")
                for row in s.type: f.write(" ".join(map(str, row)) + "\n")
                f.write(" ".join(map(str, target)) + "\n" + " ".join(map(str, wt)) + "\n")
                for k in range(nb): f.write(" ".join(map(str, forb[k])) + "\n")
        return target, forb

def tie_feasible(s, phi, nb, target, forb):
    """necessary counting check for the tied search: per phi-orbit of types."""
    tp = s.tperm(phi); seen = set()
    pw = [list(range(s.nt))]
    for k in range(1, nb): pw.append([tp[x] for x in pw[-1]])
    for t in range(s.nt):
        if t in seen: continue
        orb = []; x = t
        while x not in orb: orb.append(x); x = tp[x]
        seen.update(orb)
        if len(set(target[u] for u in orb)) > 1: return False
        if nb % len(orb): return False
        mult = nb // len(orb)
        if target[t] % mult: return False
        allowed = sum(1 for u in orb if s.osize[u] == s.m and not any(forb[k][pw[k][u]] for k in range(nb)))
        if target[t] // mult > allowed: return False
    return True

def dfs_spec(s, phi, nb, target, forb, path, order=None):
    """single tied week (week k = phi^k W): per-type cap and per-orbit need. None if infeasible."""
    tp = s.tperm(phi); pw = [list(range(s.nt))]
    for k in range(1, nb): pw.append([tp[x] for x in pw[-1]])
    orb = [-1] * s.nt; need = []; cap = [0] * s.nt
    for t in range(s.nt):
        if orb[t] >= 0: continue
        o = []; x = t
        while x not in o: o.append(x); x = tp[x]
        if len(set(target[u] for u in o)) > 1 or nb % len(o): return None
        mult = nb // len(o)
        if target[t] % mult: return None
        for u in o:
            orb[u] = len(need)
            cap[u] = int(s.osize[u] == s.m and not any(forb[k][pw[k][u]] for k in range(nb)))
        if target[t] // mult > sum(cap[u] for u in o): return None
        need.append(target[t] // mult)
    if sum(need) != 6 * s.n // 4: return None
    order = order or list(range(s.n))
    with open(path, "w") as f:
        f.write(f"{s.n} {s.nt} {len(need)}\n" + " ".join(map(str, order)) + "\n")
        for row in s.type: f.write(" ".join(map(str, row)) + "\n")
        f.write(" ".join(map(str, cap)) + "\n" + " ".join(map(str, orb)) + "\n" + " ".join(map(str, need)) + "\n")
    return True
