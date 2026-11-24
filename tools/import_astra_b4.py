#!/usr/bin/env python3
"""Import the library improvements from Astra's fourth batch (contrib/astra-2026-11-25).

3way/v24_x2 (18 oil-pattern blocks, was 19) and 3way/v24_oil_x2 (5, was 6), both at
their lower bounds. Each round 1 is asserted identical to the library's one-round file.
Usage: python3 tools/import_astra_b4.py
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "contrib" / "astra-2026-11-25"
sys.path.insert(0, str(ROOT / "tools"))
from import_astra_b2 import write, greedy  # noqa: E402

CREDIT = "Found by Astra (another AI agent), 25 Nov 2026; checked independently in contrib/astra-2026-11-25."
METHOD = ("Round 1 fixed. Round 2 is built as clash-free parts of 2, 10 and 11 weeks: the 11 weeks come from a nearly "
          "Kirkman triple system on 24 bowlers, made by doubling an order-3 invariant 12-point design; the 10 weeks have "
          "an order-3 symmetry, and the 2 opening weeks are recovered from its unmet couples. Lanes by a symmetric search, "
          "then a lane-pair permutation and bipartite flows for lanes and positions over both rounds. " + CREDIT)


def main():
    for name, r1name in [("v24_oil_x2", "v24_oil"), ("v24_x2", "v24")]:
        W = json.load(open(SRC / "3way" / f"{name}.json"))["weeks"]
        R1 = json.load(open(ROOT / "3way" / f"{r1name}.json"))["weeks"]
        assert W[:len(R1)] == R1, name
        old = json.load(open(ROOT / "3way" / f"{name}.json"))["weeks"]
        blocks = greedy(W, 3)
        assert len(blocks) < len(greedy(old, 3)), name
        g1 = greedy(R1, 3)
        lb = len(g1) - 1 + -(-(g1[-1] + len(R1)) // 11)
        assert len(blocks) == lb, name
        write("3way", name, W, 3, 2, METHOD,
              [f"Lower bound for this round 1: {len(g1) - 1} + ceil(({g1[-1]} + {len(R1)})/11) = {lb} blocks, so this is optimal."],
              blocks, round1=r1name)


if __name__ == "__main__":
    main()
