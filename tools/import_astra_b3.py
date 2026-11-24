#!/usr/bin/env python3
"""Import the library improvements from Astra's third batch (contrib/astra-2026-11-24c).

- 3way/v36_oil_x2: two rounds, round 1 = v36_oil, 5 oil patterns (16+10+12+16+16), optimal.
- hybrid/files/v27_0-1-8_mixed, v39_0-1-12_mixed: shortest hybrid seasons for 27 and 39.
- qualifying/results/astra/M3_K4_B11.json: optimal on all ten score fields.
Usage: python3 tools/import_astra_b3.py   (then rebuild qualifying/schemes.json and the pages)
"""
import json, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "contrib" / "astra-2026-11-24c"
sys.path.insert(0, str(ROOT / "tools"))
from import_astra_b2 import write, greedy, CREDIT  # noqa: E402

CREDIT = CREDIT.replace("24b", "24c")


def main():
    a = json.load(open(SRC / "3way" / "v36_oil_x2.json")); W = a["weeks"]
    R1 = json.load(open(ROOT / "3way" / "v36_oil.json"))["weeks"]
    assert W[:len(R1)] == R1
    blocks = greedy(W, 3); assert blocks == [16, 10, 12, 16, 16]
    write("3way", "v36_oil_x2", W, 3, 2,
          "Round 1 fixed. Round 2 = three 12-bowler layers with 11 internal weeks each (clash-free runs 3, 4, 4) plus "
          "two 12-week transversal systems across the layers (GF(4) on matched four-bowler groups); weeks 36-38 join "
          "round 1's 9-week tail, giving 16+10+12+16+16. Lanes by annealing inside three sets of four lane pairs, "
          "positions by bipartite flows. " + CREDIT,
          ["5 blocks is the fewest possible: a clash-free run has at most 17 weeks and 2 + ceil((9 + 35)/17) = 5."],
          blocks, round1="v36_oil")
    for f in ("v27_0-1-8_mixed.json", "v39_0-1-12_mixed.json"):
        shutil.copy(SRC / "hybrid" / f, ROOT / "hybrid" / "files" / f)
    shutil.copy(SRC / "qualifying" / "M3_K4_B11.json", ROOT / "qualifying" / "results" / "astra" / "M3_K4_B11.json")
    print("copied 2 hybrid files and 1 qualifying draw")


if __name__ == "__main__":
    main()
