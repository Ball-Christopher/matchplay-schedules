import sys, json
for line in sys.stdin:
    d = json.loads(line)
    bl = [b for f in d["fixed"] for b in f] + [b for o in d["orbit"] for b in o]
    print(" ".join(f"{c} {a}" for b in bl for c, a in b))
