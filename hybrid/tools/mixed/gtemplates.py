"""Enumerate Z_m templates (week stabiliser orders + week types) for gsat.py and run them.
usage: gtemplates.py v a2 a3 a4 m orbits timeout [--run J] [--maxspecs K]
Prints each template; with --run, runs gsat.py on all (J parallel) and saves the first sat to raw/."""
import sys, itertools, subprocess, json, os, argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from options import wtypes
ap = argparse.ArgumentParser(); ap.add_argument("v", type=int); ap.add_argument("a2", type=int); ap.add_argument("a3", type=int)
ap.add_argument("a4", type=int); ap.add_argument("m", type=int); ap.add_argument("orbits"); ap.add_argument("timeout", type=int)
ap.add_argument("--run", type=int, default=0); ap.add_argument("--tag", default=""); ap.add_argument("--all", action="store_true"); ap.add_argument("--sample", type=int, default=0)
ap.add_argument("--maxg", type=int, default=99)
A = ap.parse_args(); v, m = A.v, A.m; a = (A.a2, A.a3, A.a4); R = sum(a)
osz = []
for t in A.orbits.split(","):
    if "x" in t: s, k = map(int, t.split("x")); osz += [s] * k
    else: osz.append(int(t))
assert sum(osz) == v
tot = (v * a[0] // 2, v * a[1] // 3, v * a[2] // 4)
divs = [d for d in range(1, m + 1) if m % d == 0]
start = []; _v = 0
for s_ in osz: start.append(_v); _v += s_
orb = [o for o, s_ in enumerate(osz) for _ in range(s_)]
def g(p, i=1):
    o = orb[p]; return start[o] + (p - start[o] + i) % osz[o]
def ok_week(d, t):
    """exact check (z3, one week alone) that an H-invariant partition with t groups exists"""
    import z3
    if d == 1: return True
    step = m // d; inc = [[] for _ in range(v)]; S = z3.SolverFor("QF_FD"); seen = set(); n = 0
    for s in (2, 3, 4):
        if not t[s - 2]: continue
        L = []
        for B in itertools.combinations(range(v), s):
            if B in seen: continue
            Os = []; cur = B
            while cur not in Os: Os.append(cur); cur = tuple(sorted(g(p, step) for p in cur))
            seen.update(Os); pts = [p for b in Os for p in b]
            if len(Os) > 1 and len(set(pts)) != len(pts): continue
            x = z3.Bool(f"x{n}"); n += 1; L.append((x, len(Os)))
            for p in pts: inc[p].append((x, 1))
        if not L: return False
        S.add(z3.PbEq(L, t[s - 2]))
    for p in range(v):
        if not inc[p]: return False
        S.add(z3.PbEq(inc[p], 1))
    return S.check() == z3.sat
cands = [(d, t) for d in divs for t in wtypes(v) if all((not t[i]) or a[i] for i in range(3)) and sum(t) <= A.maxg and m // d <= R]
cands = [c for c in cands if ok_week(*c)]
if A.sample:
    import random; rng = random.Random(1); out = set(); tries = 0
    while len(out) < A.sample and tries < 200000:
        tries += 1; left = R; acc = (0, 0, 0); cur = []
        while left > 0:
            opts = [(d, t) for d, t in cands if m // d <= left and all(acc[k] + (m // d) * t[k] <= tot[k] for k in range(3))]
            if not opts: break
            d, t = rng.choice(opts); cur.append((d, t)); left -= m // d; acc = tuple(acc[k] + (m // d) * t[k] for k in range(3))
        if left == 0 and acc == tot: out.add(tuple(sorted(cur)))
    for r in sorted(out): print(" ".join(f"{d}:{t[0]},{t[1]},{t[2]}" for d, t in r))
    sys.exit()
res = []
def rec(i, left, acc, cur):
    if left == 0:
        if acc == tot: res.append(list(cur))
        return
    for j in range(i, len(cands)):
        d, t = cands[j]; c = m // d
        if c > left: continue
        nacc = tuple(acc[k] + c * t[k] for k in range(3))
        if any(nacc[k] > tot[k] for k in range(3)): continue
        cur.append((d, t)); rec(j, left - c, nacc, cur); cur.pop()
rec(0, R, (0, 0, 0), [])
print(f"v{v} {a} m{m} orbits {A.orbits}: {len(res)} templates", flush=True)
if not A.run:
    for r in res: print(" ".join(f"{d}:{t[0]},{t[1]},{t[2]}" for d, t in r))
    sys.exit()
here = os.path.dirname(os.path.abspath(__file__))
def run(r):
    specs = [f"{d}:{t[0]},{t[1]},{t[2]}" for d, t in r]
    p = subprocess.run(["python3", os.path.join(here, "gsat.py"), str(m), A.orbits, *map(str, a), str(A.timeout), *specs],
                       capture_output=True, text=True, timeout=A.timeout + 600)
    return specs, p.returncode, p.stdout, p.stderr.strip().splitlines()[-1] if p.stderr.strip() else ""
cnt = {}
with ThreadPoolExecutor(A.run) as ex:
    for fu in as_completed([ex.submit(run, r) for r in res]):
        try: specs, rc, out, err = fu.result()
        except Exception as e: print("ERR", e, flush=True); continue
        print(" ".join(specs), "->", err, flush=True); cnt[err.split()[0] if err else "?"] = cnt.get(err.split()[0] if err else "?", 0) + 1
        if rc == 0:
            fn = os.path.join(here, "raw", f"v{v}_{a[0]}-{a[1]}-{a[2]}_g{m}{A.tag}.json")
            open(fn, "w").write(out); print("FOUND", fn, flush=True)
            if not A.all: os._exit(0)
print("summary", cnt, flush=True)
