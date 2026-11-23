"""Markdown tables for the README from schemes.json / results.

    python3 report.py > results/tables.md
"""
from __future__ import annotations

import json
import os

from model import SCORE_FIELDS

HERE = os.path.dirname(os.path.abspath(__file__))
NMIX = 8  # pair_spread + 7 mixing fields


def cell(s):
    sc = s["score"]
    txt = f"{sc['max_meet']}/{sc['max_follow']}"
    if s["type"] == "rule":
        mark = "R"
    elif s["best_rule"]["ties_best_mixing"]:
        mark = "r"
    else:
        mark = "D"
    if s["proven_fields"] < 3:   # pair balance, max_meet, max_follow
        mark += "?"
    return f"{txt} {mark}"


def main():
    doc = json.load(open(os.path.join(HERE, "schemes.json")))
    S = {(s["M"], s["K"], s["B"]): s for s in doc["schemes"]}
    summ = json.load(open(os.path.join(HERE, "results", "summary.json")))
    U = {(u["M"], u["K"]): u["universal_rule"] for u in summ if "universal_rule" in u}
    base = json.load(open(os.path.join(HERE, "results", "baselines.json")))
    BL = {(b["scheme"], b["M"], b["K"], b["B"]): b for b in base}

    print("### Best achievable mixing (max meetings / max ordered follows per couple)\n")
    print("| M×K | " + " | ".join(f"B={b}" for b in range(1, 13)) + " |")
    print("|---|" + "---|" * 12)
    for K in (2, 3, 4, 5):
        for M in range(3, 11):
            print(f"| {M}×{K} | " + " | ".join(cell(S[(M, K, b)]) for b in range(1, 13)) + " |")
    print()

    print("### Zero-repeat horizon: largest B with nobody sharing a pair twice\n")
    print("| M×K | NZ rule | best rule | any draw (found) | social-golfer max (known / proven) |")
    print("|---|---|---|---|---|")
    for K in (2, 3, 4, 5):
        for M in range(3, 11):
            nzb = max([b for b in range(1, 13) if BL[("nz", M, K, b)]["score"][1] == 1] + [0])
            rb = max([b for b in range(1, 13) if S[(M, K, b)]["best_rule"]["score"][1] == 1] + [0])
            db = max([b for b in range(1, 13) if S[(M, K, b)]["score"]["max_meet"] == 1] + [0])
            s = S[(M, K, 1)]
            print(f"| {M}×{K} | {nzb} | {rb} | {db} | {s['sgp_rounds_known']} / {s['sgp_rounds_max']} |")
    print()

    print("### NZ rule versus best, g=2 (B = 3, 4, 5, 6 ⇒ N = 6, 8, 10, 12 games)\n")
    print("Cells: max meetings / max ordered follows / repeated meetings (couple-blocks beyond the first).\n")
    print("| M×K | " + " | ".join(f"NZ B={b} | best B={b}" for b in (3, 4, 5, 6)) + " |")
    print("|---|" + "---|" * 8)
    for K in (2, 3, 4, 5):
        for M in range(3, 11):
            row = []
            for b in (3, 4, 5, 6):
                nz = BL[("nz", M, K, b)]["score"]
                s = S[(M, K, b)]["score"]
                row.append(f"{nz[1]}/{nz[2]}/{nz[3]}")
                row.append(f"{s['max_meet']}/{s['max_follow']}/{s['repeats']}")
            print(f"| {M}×{K} | " + " | ".join(row) + " |")
    print()

    print("### Recommended for g = 2 (B = 3..6), K = 2, 3, 4\n")
    print("Per cell: **R** = a movement rule is as good as the best balanced draw found (on balance + all mixing "
          "fields); **D a/b (rule c/d)** = use the explicit draw from schemes.json (max meet/max follow a/b; the best "
          "lane-pair-balanced rule only manages c/d).  The rules column gives one rule in plain words covering the R cells.\n")
    print("| M×K | B=3 | B=4 | B=5 | B=6 | rule for the R cells |")
    print("|---|---|---|---|---|---|")
    from model import evaluate, rule_draw
    for K in (2, 3, 4):
        for M in range(3, 11):
            cells, rules = [], []
            for b in (3, 4, 5, 6):
                best = S[(M, K, b)]
                bs = [best["score"][x] for x in SCORE_FIELDS]
                br = best["best_rule"]
                if br["ties_best_mixing"] and br["score"][0] == bs[0]:
                    cells.append("R")
                    rules.append((b, br))
                else:
                    cells.append(f"D {bs[1]}/{bs[2]} (rule {br['score'][1]}/{br['score'][2]})")
            words = ""
            if rules:
                # one rule that is as good on every R cell, if any
                for _, cand in reversed(rules):
                    ok = all(tuple(evaluate(rule_draw(M, K, b, cand["d"], cand["pi"]))["score"][:NMIX])
                             <= tuple(S[(M, K, b)]["score"][x] for x in SCORE_FIELDS[:NMIX]) for b, _ in rules)
                    if ok:
                        words = cand["words"]
                        break
                if not words:
                    words = "; ".join(f"B={b}: {r['words']}" for b, r in rules)
            print(f"| {M}×{K} | " + " | ".join(cells) + f" | {words} |")
    print()

    print("### Universal rules (one rule, optimal among rules for every B up to the limit)\n")
    print("| M×K | optimal among rules for B ≤ | rule |")
    print("|---|---|---|")
    for K in (2, 3, 4, 5):
        for M in range(3, 11):
            u = U[(M, K)]
            print(f"| {M}×{K} | {u['optimal_for_B_up_to']} | {u['words']} |")
    print()

    print("### Where lane-pair balance forces worse mixing than the unconstrained best found\n")
    print("Mixing tuple = (max meet, max follow, repeats, follow repeats, max unordered follow, unordered follow repeats, -min meet).\n")
    for K in (2, 3, 4, 5):
        for M in range(3, 11):
            for b in range(1, 13):
                s = S[(M, K, b)]
                if s["balance_costs_mixing"]:
                    sc = [s["score"][x] for x in SCORE_FIELDS]
                    print(f"- {M}×{K} B={b}: balanced {sc[1:NMIX]} vs unconstrained {s['unconstrained_mixing']}")
    print()

    print("### Open: max meetings or max follows not proven optimal\n")
    print("Tuple = (pair_spread, max_meet, max_follow, repeats, follow_repeats, max_ufollow, ufollow_repeats, -min_meet); bound = simple counting bound, or z3 where run.\n")
    for K in (2, 3, 4, 5):
        for M in range(3, 11):
            for b in range(1, 13):
                s = S[(M, K, b)]
                if s["proven_fields"] < 3:
                    f = SCORE_FIELDS[s["proven_fields"]]
                    sc = [s["score"][x] for x in SCORE_FIELDS]
                    print(f"- {M}×{K} B={b}: best {sc[:NMIX]} vs bound {s['lower_bound'][:NMIX]} (first gap: {f})")


if __name__ == "__main__":
    main()
