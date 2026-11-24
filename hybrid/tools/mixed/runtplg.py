"""Run ggsat.py over templates in a file. usage: runtplg.py GROUP c f a2 a3 a4 timeout J tplfile tag"""
import sys, subprocess, os
from concurrent.futures import ThreadPoolExecutor, as_completed
grp, c, f, a2, a3, a4, tmo, J, fn, tag = sys.argv[1:11]
here = os.path.dirname(os.path.abspath(__file__))
tpls = [l.split() for l in open(fn) if ":" in l and not l.startswith("v")]
def run(sp):
    p = subprocess.run(["python3", os.path.join(here, "ggsat.py"), grp, c, f, a2, a3, a4, tmo, *sp], capture_output=True, text=True)
    return sp, p.returncode, p.stdout, (p.stderr.strip().splitlines() or [""])[-1]
with ThreadPoolExecutor(int(J)) as ex:
    for fu in as_completed([ex.submit(run, sp) for sp in tpls]):
        sp, rc, out, err = fu.result(); print(" ".join(sp), "->", err, flush=True)
        if rc == 0:
            v = int(c) * 0
            open(os.path.join(here, "raw", f"gg_{grp}_{a2}-{a3}-{a4}{tag}.json"), "w").write(out); print("FOUND", flush=True); os._exit(0)
print("done", flush=True)
