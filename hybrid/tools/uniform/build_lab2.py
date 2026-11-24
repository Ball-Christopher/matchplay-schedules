"""Write a file from a labeled2.py result (out/lab2_<tag>_<seed>.json).
usage: python3 build_lab2.py <result json> <file name> [lane seconds]"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import finish
from regroup import mix
HERE = os.path.dirname(os.path.abspath(__file__))
src, fn = sys.argv[1], sys.argv[2]; secs = float(sys.argv[3]) if len(sys.argv) > 3 else 60
d = json.load(open(os.path.join(HERE, 'out', src)))
u, g, lam, W = d['u'], d['g'], d['lam'], d['weeks']
gs = f'{g * lam}-way'
sizes = sorted(len(b[0]) for b in d['labeled'])
meth = (f'labeled uniformly resolvable design on {u} points' + (f' with {u//g} groups of {g}' if g > 1 else '') +
        f', Z_{lam} labels, block sizes {sizes} (found by z3, labeled2.py), expanded by {lam} (each point -> {lam} bowlers; Shen / Schuster 2009 Thm 2.2); '
        f'the {u//g} expanded groups of {g*lam} form one more {gs} week; 2-way weeks wrapped two matches per lane pair where needed')
v = u * lam; a = mix(W)
assert fn == f'v{v}_{a[0]}-{a[1]}-{a[2]}.json', (fn, a)
finish(v, W, fn, meth, seconds=secs, procs=2)
