"""36 oil in 4 blocks, general symmetric search. Z_9 x 4; alpha: (c,i)->(pi c, mu i + s_c) with alpha^3 in Z_9.
Base weeks W, aW, a^2W (each Z_9-orbit one block). Fourth block F = 8 base blocks (each developed mod 9), alpha-closed,
all 48 pair types distinct, grouped into weeks: a transversal block = one invariant week; three blocks whose 12 points
(after translations) represent every <3>-coset = one week V fixed by i->i+3 with orbit V, V+1, V+2.
Usage: f36c.py enum PI mu s0,s1,s2,s3 out.json [max]   |   f36c.py dfs in.json nodelimit part nparts"""
import sys, random, subprocess, json, itertools
from gen import *
S = Sys(9, 4, 0)
def canon(B): return min(tuple(sorted(S.sh(p, k) for p in B)) for k in range(9))
def types(B): return [S.type[a][b] for a, b in itertools.combinations(B, 2)]
def is_tr(B): return len({p // 9 for p in B}) == 4
def triple_shifts(Bs):
    for t in itertools.product(range(3), repeat=2):
        tr = [list(Bs[0]), [S.sh(p, t[0]) for p in Bs[1]], [S.sh(p, t[1]) for p in Bs[2]]]
        if len({(p // 9, p % 3) for B in tr for p in B}) == 12: return tr
    return None
def group_weeks(blocks):
    """partition into weeks: ('tr', B) or ('wk3', [B1,B2,B3]); None if impossible"""
    nt = [b for b in blocks if not is_tr(b)]
    if not nt: return [("tr", list(b)) for b in blocks]
    b0 = nt[0]; rest = [b for b in blocks if b != b0]
    for x, y in itertools.combinations(rest, 2):
        tr = triple_shifts([b0, x, y])
        if tr:
            sub = group_weeks([b for b in rest if b != x and b != y])
            if sub is not None: return [("wk3", tr)] + sub
    return None
def mk_alpha(PI, mu, sv): return [S.pt(PI[p // 9], mu * (p % 9) + sv[p // 9]) for p in range(36)]
def weeks_of(F):
    inv = []; extra = []
    for kind, b in F:
        if kind == "tr": inv.append([[S.sh(p, k) for p in b] for k in range(9)])
        else: extra.append(b)
    return inv, extra
if __name__ == "__main__" and sys.argv[1] == "enum":
    PI = [0, 2, 3, 1] if sys.argv[2] == "1" else [0, 1, 2, 3]; mu = int(sys.argv[3]); sv = list(map(int, sys.argv[4].split(",")))
    mx = int(sys.argv[6]) if len(sys.argv) > 6 else 300
    alpha = mk_alpha(PI, mu, sv); a3 = [alpha[alpha[alpha[p]]] for p in range(36)]
    assert len({(a3[p] - p) % 9 for p in range(36)}) == 1 and all(a3[p] // 9 == p // 9 for p in range(36))
    rng = random.Random(1); orbs = {}; seen = set()
    for B in itertools.combinations(range(36), 4):
        cb = canon(B)
        if cb in seen: continue
        o = [cb]
        for _ in range(2):
            x = canon([alpha[p] for p in o[-1]])
            if x not in o: o.append(x)
        seen.update(o)
        ts = [t for b in o for t in types(b)]
        if len(set(ts)) != 6 * len(o): continue
        orbs[min(o)] = (o, sum(1 << t for t in ts))
    fixed = [o for o in orbs.values() if len(o[0]) == 1]; full = [o for o in orbs.values() if len(o[0]) == 3]
    print("fixed", len(fixed), "full", len(full), flush=True)
    rng.shuffle(fixed); rng.shuffle(full); out = []; cnt = [0, 0, 0]
    def fsets(k, start=0, mask=0, acc=()):
        if k == 0: yield acc, mask; return
        for i in range(start, len(fixed)):
            if not fixed[i][1] & mask: yield from fsets(k - 1, i + 1, mask | fixed[i][1], acc + (fixed[i],))
    for nf in (2, 5, 8):
        for fs, m in fsets(nf):
            ok = [g for g in full if not g[1] & m]
            for gs in itertools.combinations(ok, (8 - nf) // 3):
                mm = m; good = True
                for g in gs:
                    if g[1] & mm: good = False; break
                    mm |= g[1]
                if not good: continue
                cnt[0] += 1
                blocks = [b for o in fs + gs for b in o[0]]
                F = group_weeks(blocks)
                if F is None: continue
                cnt[1] += 1
                inv, extra = weeks_of(F)
                r = S.spec(alpha, 3, 3, inv, [-1] * len(inv), None, extra=extra)
                if not r or not dfs_spec(S, alpha, 3, r[0], r[1], "/dev/null"): continue
                cnt[2] += 1; out.append(F)
                if len(out) >= mx: break
            if len(out) >= mx: break
        print("nf", nf, "type-disjoint/weeks ok/count ok", cnt, flush=True)
    json.dump({"pi": PI, "mu": mu, "s": sv, "F": out}, open(sys.argv[5], "w"))
if __name__ == "__main__" and sys.argv[1] == "dfs":
    d = json.load(open(sys.argv[2])); lim = sys.argv[3]; part, nparts = int(sys.argv[4]), int(sys.argv[5])
    alpha = mk_alpha(d["pi"], d["mu"], d["s"]); tag = sys.argv[2].replace(".json", "")
    for n, F in enumerate(d["F"]):
        if n % nparts != part: continue
        inv, extra = weeks_of(F); path = f"s_{tag}_{part}.txt"
        r = S.spec(alpha, 3, 3, inv, [-1] * len(inv), None, extra=extra)
        dfs_spec(S, alpha, 3, r[0], r[1], path)
        out = subprocess.run(["./dfs", path, lim, "1", str(n + 1)], capture_output=True, text=True).stdout
        sol = [l for l in out.splitlines() if l.startswith("SOL")]
        print(n, [k for k, b in F], out.splitlines()[-1], flush=True)
        if sol:
            json.dump({"pi": d["pi"], "mu": d["mu"], "s": d["s"], "F": F, "sol": sol[0]}, open(f"sol_{tag}_{n}.json", "w")); print("FOUND", flush=True)
