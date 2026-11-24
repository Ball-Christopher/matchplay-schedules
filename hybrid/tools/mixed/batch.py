"""Launch orbit-annealer runs for one case over several base-type combos/seeds/temperatures; save first success.
usage: batch.py name m c f a2 a3 a4 nbase "INV1" ["INV2" ...] -- secs ncombos seeds temps"""
import sys, subprocess, itertools, os, json
from concurrent.futures import ThreadPoolExecutor, as_completed
from options import wtypes
args = sys.argv[1:]; k = args.index("--")
name, m, c, f, a2, a3, a4, nb = args[0], *map(int, args[1:8]); invs = args[8:k]
secs, ncomb, seeds = map(int, args[k+1:k+4]); temps = args[k+4].split(",")
v = c*m + f; R = a2 + a3 + a4
def invtype(desc):
    t = [0, 0, 0]
    for part in desc.split(";"):
        if part[0] == "T": t[len(part[1:].split(","))-2] += m
        elif part[0] == "W": t[m + ("+" in part) - 2] += 1
        elif part[0] == "U": t[m*len(part[1:].split(",")) - 2] += 1
        elif part[0] == "P": t[len(part[1:].split(",")) - 2] += 1
    return t
tot = [v*a2//2, v*a3//3, v*a4//4]
for d in invs:
    t = invtype(d); tot = [x - y for x, y in zip(tot, t)]
assert all(x % m == 0 for x in tot), tot
tot = [x//m for x in tot]
combs = [cm for cm in itertools.combinations_with_replacement(wtypes(v), nb) if list(map(sum, zip(*cm))) == tot]
maxg = max(sum(invtype(d)) for d in invs) if invs else 0
combs.sort(key=lambda cm: (max(maxg, max(sum(t) for t in cm)), sum(t[0] for t in cm)))
print(name, "combos", len(combs), combs[:ncomb], flush=True)
jobs = []
for ci, cm in enumerate(combs[:ncomb]):
    cfg = f"cfg_{name}_{ci}.txt"
    out = subprocess.run(["python3", "mkcfg.py", *map(str, (m, c, f, a2, a3, a4)), *[f"F:{t[0]},{t[1]},{t[2]}" for t in cm], *[f"I:{d}" for d in invs]], capture_output=True, text=True).stdout
    open(cfg, "w").write(out)
    for s in range(1, seeds+1):
        for T in temps: jobs.append((cfg, s, T))
done = False
def run(j):
    cfg, s, T = j
    p = subprocess.run(["./oanneal", str(s), str(secs)], stdin=open(cfg), capture_output=True, text=True, env={**os.environ, "T0": T, "TMIN": T})
    return j, p.returncode, p.stdout, p.stderr.strip()
with ThreadPoolExecutor(int(os.environ.get("J", "8"))) as ex:
    futs = [ex.submit(run, j) for j in jobs]
    for fu in as_completed(futs):
        j, rc, out, err = fu.result(); print(name, j, err, flush=True)
        if rc == 0:
            json.dump({"weeks": json.loads(out), "cfg": open(j[0]).read(), "T": j[2]}, open(f"raw/{name}.json", "w"))
            print("FOUND", name, flush=True); os._exit(0)
print("NOTFOUND", name)
