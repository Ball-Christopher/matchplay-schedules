"""Compile and reproduce the 19 orbit enumerations using GNU C++17."""
import subprocess
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parent
expected = (root/'symmetry15_expected.txt').read_text().splitlines()
cases = {(p,a,b) for p in (2,3,5) for a in range(6//p+1)
         for b in range(5//p+1) if a or b}
assert {tuple(map(int,line.split()[:3])) for line in expected} == cases
with tempfile.TemporaryDirectory() as folder:
    exe = str(Path(folder)/'symmetry')
    subprocess.run(['g++','-O3','-std=c++17',str(root/'symmetry15.cpp'),'-o',exe], check=True)
    for line in expected:
        result = subprocess.check_output([exe,*line.split()[:3]], text=True).strip()
        assert result == line and result.split()[-1] == '0'
        print(result, flush=True)
