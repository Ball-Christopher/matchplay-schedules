"""Generate all reduced prefix cases and check them with the C++ enumerator."""
from itertools import combinations_with_replacement, permutations
from pathlib import Path
import subprocess
import tempfile

def profiles():
    pairs=[(x,y) for y in range(4) for x in range(y)]
    relabel=[[pairs.index(tuple(sorted((p[x],p[y])))) for x,y in pairs] for p in permutations(range(4))]
    for total in range(6):
        cases=set()
        for multiset in combinations_with_replacement(range(6),total):
            counts=[multiset.count(i) for i in range(6)]
            cases.add(max(''.join(str(counts[j]) for j in perm) for perm in relabel))
        yield from sorted(cases,reverse=True)
    yield '111111'

if __name__=='__main__':
    root=Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory() as tmp:
        exe=str(Path(tmp)/'verify')
        subprocess.run(['g++','-O3','-std=c++17',str(root/'verify.cpp'),'-o',exe],check=True)
        for case in profiles():
            row=subprocess.check_output([exe,case],text=True).strip()
            assert row.split()[0]==case and row.split()[-1]=='0', row
            print(row,flush=True)
