import sys, json, random, subprocess
from gen32 import *
from lanes import solve
out = subprocess.run(["./sa", "s32a.txt", sys.argv[1], "2000000", "2.0", "0.1", "0", "4"], capture_output=True, text=True).stdout
rng = random.Random(int(sys.argv[1]))
for line in out.splitlines():
    if not line.startswith("SOL"): continue
    base = [[list(map(int, x.split()))[i:i+4] for i in range(0, 32, 4)] for x in line.split("|")[1:]]
    W = solve(7, 4, base, [(0,0,0,0),(0,1,0,1),(0,6,0,6)], 31, rng)
    print("lanes", W is not None)
    if W:
        json.dump({"weeks": W, "base": base, "tr": [(0,0,0,0),(0,1,0,1),(0,6,0,6)], "half": []}, open(f"d32a_{sys.argv[1]}.json", "w")); break
