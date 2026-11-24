"""Random conversion search: take a design, remove a random choice of some of its classes
and re-resolve their pairs into classes of other sizes (regroup.py).

usage: python3 convsearch.py SRC TAKE TO [timeout_per_try] [tries] [seed]
  SRC  : a file in hybrid/files (e.g. v36_0-4-9.json), or gen:<template>  (a fresh design
         from cyclic.py templates each try: rgdd3_8, nkts24, rgdd4_6 (3-RGDD 4^6 + groups))
         or out:<file> (JSON list of weeks, 1-based, in tools/uniform/out)
  TAKE : sizes of the classes to remove, e.g. 3,3,3,4,4  (chosen at random among the classes
         of that size)
  TO   : sizes of the new classes, e.g. 4,4,4,4
Writes the first success to out/conv_<v>_<a2>-<a3>-<a4>_<seed>.json and stops."""
import json, os, random, sys, time, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from regroup import load_weeks, convert, mix
from common import check_design
HERE = os.path.dirname(os.path.abspath(__file__))

def gen(name, seed):
    if name in ('rtd36', 'rtd32'):
        import rtd
        q = 9 if name == 'rtd36' else 8
        W = rtd.v36_049() if q == 9 else rtd.v32_409()
        rng = random.Random(seed); perm = {}
        for i in range(4):
            ys = list(range(q)); rng.shuffle(ys)
            for y in range(q): perm[1 + i * q + y] = 1 + i * q + ys[y]
        return W[:q] + [[[perm[p] for p in g] for g in wk] for wk in W[q:]]
    from cyclic import search_c, to_one_based
    argv = sys.argv; sys.argv = argv[:1]
    import try_cyclic
    sys.argv = argv
    if name == 'rgdd4_6':
        m, rows, f, ks, half = 5, 4, 4, [3, 3], False
    else:
        m, rows, f, ks, half = try_cyclic.cases[name]
    fx = try_cyclic.groups_fixed(m, rows, f, half)
    W = search_c(m, rows, f, ks, fx, seed=seed, node_limit=2000000, time_limit=60)
    return to_one_based(W) if W else None

def main():
    src, take, to = sys.argv[1], [int(x) for x in sys.argv[2].split(',')], [int(x) for x in sys.argv[3].split(',')]
    to_s = float(sys.argv[4]) if len(sys.argv) > 4 else 30
    tries = int(sys.argv[5]) if len(sys.argv) > 5 else 100
    seed = int(sys.argv[6]) if len(sys.argv) > 6 else 1
    rng = random.Random(seed)
    base = None
    if src.startswith('out:'): base = json.load(open(os.path.join(HERE, 'out', src[4:])))
    elif not src.startswith('gen:'): base = load_weeks(src)[1]
    stats = collections.Counter(); t0 = time.time()
    for t in range(tries):
        W = base if base else gen(src[4:], seed * 1000 + t)
        if W is None: stats['gen-fail'] += 1; continue
        byk = collections.defaultdict(list)
        for i, wk in enumerate(W): byk[len(wk[0])].append(i)
        need = collections.Counter(take); idx = []
        for k, c in need.items(): idx += rng.sample(byk[k], c)
        r = convert(W, idx, to, timeout=to_s, seed=rng.randrange(10 ** 9))
        if r is None: stats['none'] += 1
        elif r == 'timeout': stats['timeout'] += 1
        else:
            v = sum(len(g) for g in r[0]); check_design(v, r)
            a = mix(r); fn = os.path.join(HERE, 'out', f'conv_{v}_{a[0]}-{a[1]}-{a[2]}_{seed}.json')
            json.dump(r, open(fn, 'w'))
            print('FOUND', a, 'try', t, 'idx', sorted(idx), round(time.time() - t0, 1), fn, flush=True)
            return
        if t % 10 == 9: print(t + 1, dict(stats), round(time.time() - t0, 1), flush=True)
    print('not found', dict(stats), round(time.time() - t0, 1), flush=True)

if __name__ == '__main__':
    main()
