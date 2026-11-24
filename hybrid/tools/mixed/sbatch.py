"""Run sanneal on Z_m templates: random H-invariant initial base weeks (random shapes), many seeds, J parallel.
usage: sbatch.py name m orbits a2 a3 a4 secs seeds J temps spec... [--templates file]  spec = d:g2,g3,g4
  temps comma list of T (T0=TMIN=T). With spec 'FILE:path', each line of path is a template (round-robin over templates).
Saves first success to raw/{name}.json."""
import sys, random, itertools, subprocess, json, os
from concurrent.futures import ThreadPoolExecutor, as_completed
here = os.path.dirname(os.path.abspath(__file__))
name, m, orbits, a2, a3, a4, secs, seeds, J, temps = sys.argv[1:11]
m, a2, a3, a4, secs, seeds, J = int(m), int(a2), int(a3), int(a4), int(secs), int(seeds), int(J)
temps = temps.split(","); specargs = sys.argv[11:]
osz = []
for t in orbits.split(","):
    if "x" in t: s, k = map(int, t.split("x")); osz += [s] * k
    else: osz.append(int(t))
start = []; v = 0
for s in osz: start.append(v); v += s
orb = [o for o, s in enumerate(osz) for _ in range(s)]
def g(p, i=1):
    o = orb[p]; return start[o] + (p - start[o] + i) % osz[o]
def parse(specs): return [(int(s.split(":")[0]), tuple(map(int, s.split(":")[1].split(",")))) for s in specs]
if specargs and specargs[0].startswith("FILE:"):
    templates = [parse(l.split()) for l in open(specargs[0][5:]) if l.strip() and ":" in l and "->" not in l and not l.startswith("v")]
else: templates = [parse(specargs)]
def rand_week(d, t, rng, tries=20000):
    step = m // d
    for _ in range(tries):
        left = set(range(v)); cnt = {2: t[0], 3: t[1], 4: t[2]}; groups = []; ok = True
        while left:
            p = min(left, key=lambda x: (rng.random(), x)) if rng.random() < 0.5 else min(left)
            opts = [s for s in (2, 3, 4) if cnt[s] > 0]; rng.shuffle(opts); placed = False
            for s in opts:
                for _ in range(60):
                    B = tuple(sorted([p] + rng.sample(sorted(left - {p}), s - 1))) if len(left) >= s else None
                    if B is None: break
                    Os = []; cur = B
                    while cur not in Os: Os.append(cur); cur = tuple(sorted(g(x, step) for x in cur))
                    pts = [x for b in Os for x in b]
                    if len(set(pts)) != len(pts) and len(Os) > 1: continue
                    if not set(pts) <= left or len(Os) > cnt[s]: continue
                    groups += [list(b) for b in Os]; left -= set(pts); cnt[s] -= len(Os); placed = True; break
                if placed: break
            if not placed: ok = False; break
        if ok: return groups
    return None
def cfg(tpl, rng):
    lines = [f"{m}", f"{len(osz)} " + " ".join(map(str, osz)), f"{a2} {a3} {a4}", f"{len(tpl)}"]
    for d, t in tpl:
        W = rand_week(d, t, rng)
        if W is None: return None
        lines.append(f"{d} {len(W)}  " + "  ".join(f"{len(b)} " + " ".join(map(str, b)) for b in W))
    return "\n".join(lines) + "\n"
jobs = []
for s in range(1, seeds + 1):
    for ti, tpl in enumerate(templates):
        for T in temps: jobs.append((ti, s, T))
def run(j):
    ti, s, T = j; rng = random.Random(s * 1000 + ti); c = cfg(templates[ti], rng)
    if c is None: return j, 9, "", "no initial partition"
    p = subprocess.run([os.path.join(here, "sanneal"), str(s), str(secs)], input=c, capture_output=True, text=True,
                       env={**os.environ, "T0": T, "TMIN": T})
    return j, p.returncode, p.stdout, p.stderr.strip() + ("" if p.returncode else "\n" + c)
print(name, "templates", len(templates), "jobs", len(jobs), flush=True)
with ThreadPoolExecutor(J) as ex:
    for fu in as_completed([ex.submit(run, j) for j in jobs]):
        j, rc, out, err = fu.result()
        print(name, " ".join(f"{d}:{t[0]},{t[1]},{t[2]}" for d, t in templates[j[0]]), j[1:], err.splitlines()[0] if err else "", flush=True)
        if rc == 0:
            json.dump({"weeks": json.loads(out), "m": m, "orbits": osz, "template": templates[j[0]], "T": j[2], "seed": j[1]},
                      open(os.path.join(here, "raw", f"{name}.json"), "w"))
            print("FOUND", name, flush=True); os._exit(0)
print("NOTFOUND", name, flush=True)
