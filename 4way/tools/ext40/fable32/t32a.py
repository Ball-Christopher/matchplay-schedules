from gen32 import *
phi = phi32(1)
inv = [S.transversal(x) for x in [(0,0,0,0),(0,1,0,1),(0,6,0,6)]]
r = S.spec(phi, 4, True, inv, (-1,-1,-1), "s32a.txt", oil=False)
print(r is not None, tie_feasible(S, phi, 4, *r))
