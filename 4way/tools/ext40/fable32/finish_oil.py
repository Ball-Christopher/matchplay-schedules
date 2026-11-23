"""Write an oil file from a design JSON that already carries its blocks (weeks listed block by block).
Usage: python3 finish_oil.py N design.json method.txt [steps] [seed] [--dry]"""
import sys, json, random
sys.path.insert(0, '..')
from finish import *
def finish_oil_blocks(N, path, method, steps=40000, seed=1, dry=False):
    rng = random.Random(seed)
    d = json.load(open(path)); W = [[[p + 1 for p in g] for g in wk] for wk in d["weeks"]]; blocks = d["blocks"]
    v = 4 * len(W[0]); assert v == N; real = list(range(1, v + 1))
    assert block_repeats(W, blocks) == 0
    W1, blocks = order_blocks(W, v, real, blocks, rng, steps)
    W1 = assign(W1, 4)
    rp = block_repeats(W1, blocks); st = stats(W1, v, 4); lam = st["meet"][0]
    print(f"v{N}_oil: blocks {blocks} repeats {rp} lanes off {st['lane_off']} worst prefix {max(st['prefix_spread'][:-1])} sumsq {sum(x*x for x in st['prefix_spread'])}")
    if dry: return
    hdr = f"# {v} players, 4 per lane pair, {len(W1)} weeks: every couple meets exactly {lam} times.\n"
    hdr += f"# Oil-pattern blocks (consecutive weeks): {' + '.join(map(str, blocks))} = {len(W1)} weeks.\n"
    i = 1
    for n_, b in enumerate(blocks): hdr += f"#   block {n_ + 1}: weeks {i}-{i + b - 1}\n"; i += b
    hdr += f"# Same-block repeat meetings: {rp}" + (f" (no couple meets twice on one pattern; every couple meets on {lam} different patterns)" if rp == 0 else "") + ".\n"
    hdr += f"# Lane pairs: {'exact (floor/ceil for every bowler)' if st['lane_off'] == 0 else str(st['lane_off']) + ' bowler(s) off'}.\n"
    st = write(str(OUT), f"v{N}_oil", W1, v, 4, 1, method, hdr)
    o = json.load(open(OUT / f"v{N}_oil.json")); o["blocks"] = blocks; o["block_repeats"] = rp
    o["notes"] = "design (0-based points m*class+i, fixed bowlers last): " + json.dumps({k: d[k] for k in d if k not in ("weeks", "blocks")})
    json.dump(o, open(OUT / f"v{N}_oil.json", "w"), indent=1)
if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if x != "--dry"]
    finish_oil_blocks(int(a[0]), a[1], open(a[2]).read().strip(), int(a[3]) if len(a) > 3 else 40000, int(a[4]) if len(a) > 4 else 1, "--dry" in sys.argv)
