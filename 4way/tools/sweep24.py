import json, time, sys
import gen_designs as G, order_search as O
best = None; t0 = time.time(); s = 0; seen = set()
while time.time() - t0 < float(sys.argv[1]):
    s += 1
    W, b = G.rotational(24, 23, 3, seed=1000 + s)
    key = tuple(sorted(tuple(x) for x in b))
    if key in seen: continue
    seen.add(key)
    seq, h = O.beam_order(24, W, beam=150)
    score = (max(h), sum(h))
    print(s, score, h, flush=True)
    if best is None or score < best[0]:
        best = (score, [W[i] for i in seq], b, h)
        json.dump({"weeks": best[1], "base": b, "spreads": h}, open("sweep24_best.json", "w"))
print("BEST", best[0], best[3])
