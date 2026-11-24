"""Derive further uniform mixes from the uniform files already in hybrid/files by local
re-resolutions (regroup.py), breadth first:
  Q -> MMM          a 4-way week split into three 2-way weeks (always possible)
  TT -> MMMM        two 3-way weeks re-resolved as four 2-way weeks
  TT -> MMT, MT -> MMM, TQ -> MMMMM, TTQ -> MQQ, TQQ -> MMQQ, TTTTQ -> MMQQQ
(M/T/Q = 2/3/4-way week).  Only mixes with R <= RMAX and no file yet are kept.
usage: python3 derived.py v [v ...]   (writes files; lanes by lanes.c)"""
import glob, json, os, random, re, sys, collections, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from regroup import load_weeks, convert, split4, mix
from common import finish, HYB
RMAX = 14
MOVES = [('Q', 'MMM'), ('TT', 'MMMM'), ('TT', 'MMT'), ('MT', 'MMM'), ('TQ', 'MMMMM'), ('TTQ', 'MQQ'),
         ('TQQ', 'MMQQ'), ('TTTTQ', 'MMQQQ')]
SZ = {'M': 2, 'T': 3, 'Q': 4}
NAME = {(): ''}

def apply(W, src, dst, rng, tries=6, timeout=10):
    byk = collections.defaultdict(list)
    for i, wk in enumerate(W): byk[len(wk[0])].append(i)
    need = collections.Counter(SZ[c] for c in src)
    if any(len(byk[k]) < c for k, c in need.items()): return None
    for _ in range(tries):
        idx = [i for k, c in need.items() for i in rng.sample(byk[k], c)]
        if (src, dst) == ('Q', 'MMM'):
            return [wk for i, wk in enumerate(W) if i != idx[0]] + split4(W[idx[0]])
        r = convert(W, idx, [SZ[c] for c in dst], timeout=timeout, seed=rng.randrange(10 ** 9))
        if isinstance(r, list): return r
    return None

def run(v, seconds=20):
    rng = random.Random(v)
    have = {}
    for f in sorted(glob.glob(os.path.join(HYB, 'files', f'v{v}_*.json'))):
        b = os.path.basename(f)
        if 'mixed' in b or 'archive' in b: continue
        vv, W = load_weeks(b); have[mix(W)] = (W, b)
    queue = list(have.items()); found = {}
    while queue:
        m0, (W, how) = queue.pop(0)
        for src, dst in MOVES:
            a = list(m0)
            for c in src: a[SZ[c] - 2] -= 1
            for c in dst: a[SZ[c] - 2] += 1
            a = tuple(a)
            if min(a) < 0 or sum(a) > RMAX or a in have or a in found: continue
            r = apply(W, src, dst, rng)
            if r is None: print(v, m0, src, '->', dst, 'failed', flush=True); continue
            desc = f'{how} with {src}->{dst}'
            found[a] = (r, desc); queue.append((a, (r, desc)))
            print(v, 'new', a, 'from', desc, flush=True)
    for a, (W, desc) in sorted(found.items()):
        fn = f'v{v}_{a[0]}-{a[1]}-{a[2]}.json'
        meth = ('derived from ' + desc.replace('.json', '') + ' (M/T/Q = 2/3/4-way week; Q->MMM splits a K4 week into its three matchings, '
                'other moves re-resolve the couples of the removed weeks by exact cover, tools/uniform/derived.py); 2-way weeks wrapped two matches per lane pair where needed')
        finish(v, W, fn, meth, seconds=seconds, procs=2)

if __name__ == '__main__':
    for v in sys.argv[1:]: run(int(v))
