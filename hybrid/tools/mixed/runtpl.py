"""Run gsat.py over the templates in a file. usage: runtpl.py v a2 a3 a4 m orbits timeout J tplfile tag"""
import sys, subprocess, os
from concurrent.futures import ThreadPoolExecutor, as_completed
v, a2, a3, a4, m, orbits, tmo, J, fn, tag = sys.argv[1:11]
here = os.path.dirname(os.path.abspath(__file__))
tpls = [l.split() for l in open(fn) if ":" in l and "templates" not in l]
def run(sp):
    p = subprocess.run(["python3", os.path.join(here, "gsat.py"), m, orbits, a2, a3, a4, tmo, *sp], capture_output=True, text=True)
    return sp, p.returncode, p.stdout, (p.stderr.strip().splitlines() or [""])[-1]
with ThreadPoolExecutor(int(J)) as ex:
    for fu in as_completed([ex.submit(run, sp) for sp in tpls]):
        sp, rc, out, err = fu.result(); print(" ".join(sp), "->", err, flush=True)
        if rc == 0:
            open(os.path.join(here, "raw", f"v{v}_{a2}-{a3}-{a4}_g{m}{tag}.json"), "w").write(out); print("FOUND", flush=True); os._exit(0)
print("done", flush=True)
