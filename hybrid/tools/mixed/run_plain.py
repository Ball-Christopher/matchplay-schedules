"""Run the plain annealer on several week-type multisets in parallel; save first success to raw/."""
import sys, subprocess, json, os, itertools
from concurrent.futures import ThreadPoolExecutor, as_completed
from options import solutions
v = int(sys.argv[1]); a = tuple(map(int, sys.argv[2:5])); secs = sys.argv[5]; nsets = int(sys.argv[6]); seeds = int(sys.argv[7])
R = sum(a); sols = solutions(v, R, a, limit=400)
# prefer multisets with few distinct week types
sols.sort(key=lambda s: (max(sum(t) for t, k in s), len(s), -max(k for t, k in s)))
jobs = [(s, seed) for s in sols[:nsets] for seed in range(1, seeds+1)]
os.makedirs("raw", exist_ok=True)
def run(job):
    s, seed = job
    args = ["./anneal", str(v), *map(str, a), str(seed), secs] + [f"{t[0]},{t[1]},{t[2]}x{k}" for t, k in s]
    p = subprocess.run(args, capture_output=True, text=True)
    return job, p.returncode, p.stdout, p.stderr.strip()
with ThreadPoolExecutor(int(os.environ.get("J", "16"))) as ex:
    for f in as_completed([ex.submit(run, j) for j in jobs]):
        (s, seed), rc, out, err = f.result()
        print(s, seed, rc, err, flush=True)
        if rc == 0:
            fn = f"raw/v{v}_{a[0]}-{a[1]}-{a[2]}_plain.json"
            json.dump({"v": v, "a": a, "types": s, "weeks": json.loads(out)}, open(fn, "w"))
            print("saved", fn); os._exit(0)
