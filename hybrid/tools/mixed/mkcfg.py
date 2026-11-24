"""Make an oanneal config. usage: mkcfg.py m c f a2 a3 a4 "F:g2,g3,g4" ... "I:desc"
I desc: ';'-separated parts: T<a,b,..> transversal set (m groups {(x,a),(x,b)..}), W<a> whole class,
 W<a>+<j> whole class plus fixed point j, P<i,j..> fixed-point group."""
import sys
m, c, f, a2, a3, a4 = map(int, sys.argv[1:7]); ents = []
for s in sys.argv[7:]:
    k, body = s.split(":", 1)
    if k == "F": ents.append("F " + body.replace(",", " "))
    else:
        groups = []
        for part in body.split(";"):
            if part[0] == "T":
                cl = list(map(int, part[1:].split(",")))
                for x in range(m): groups.append([a*m + x for a in cl])
            elif part[0] == "W":
                if "+" in part: a, j = part[1:].split("+"); groups.append([int(a)*m + x for x in range(m)] + [c*m + int(j)])
                else: groups.append([int(part[1:])*m + x for x in range(m)])
            elif part[0] == "U": groups.append([int(a)*m + x for a in part[1:].split(",") for x in range(m)])
            elif part[0] == "P": groups.append([c*m + int(j) for j in part[1:].split(",")])
        assert sorted(p for g in groups for p in g) == list(range(c*m+f)), groups
        ents.append(f"I {len(groups)} " + "  ".join(f"{len(g)} " + " ".join(map(str, g)) for g in groups))
print(m, c, f, a2, a3, a4, len(ents)); print("\n".join(ents))
