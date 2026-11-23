"""Combine rule search, annealed designs and baselines into schemes.json.

    python3 build_schemes.py      -> schemes.json, results/summary.json

For each (M, K, B) the recommended scheme is the better (lexicographically,
model.SCORE_FIELDS) of the best movement rule and the best unrestricted draw;
a rule wins ties (simplicity).
"""
from __future__ import annotations

import json
import os

from model import MIXING_FIELDS, SCORE_FIELDS, describe_rule, evaluate, rule_draw, rule_exclusion
from optimum import SGP, bounds, rule_best
from baselines import schemes as baseline_rules

HERE = os.path.dirname(os.path.abspath(__file__))
NMIX = 1 + len(MIXING_FIELDS)  # pair balance + mixing fields (pairings, following, min meet)


def relabel(draw):
    """Renumber bowlers 1..MK by their block-1 seat (pair, position)."""
    first = [x for pr in draw[0] for x in pr]
    rel = {a: i + 1 for i, a in enumerate(first)}
    return [[[rel[x] for x in pr] for pr in blk] for blk in draw]


def universal(M, K):
    for line in open(os.path.join(HERE, "results", "rules", f"M{M}_K{K}.jsonl")):
        r = json.loads(line)
        if r["kind"] == "universal":
            return r


EXACT = {}
for _f in ("exact_first.json", "exact.json", "exact_b7.json"):
    _ep = os.path.join(HERE, "results", _f)
    if os.path.exists(_ep):
        EXACT.update(json.load(open(_ep)))


def main():
    out, summary = [], []
    for K in (2, 3, 4, 5):
        for M in range(3, 11):
            uni = universal(M, K)
            for B in range(1, 13):
                lb, known = bounds(M, K, B)
                # exact (z3) bound on max_meet under lane-pair balance, if run
                ex_log = EXACT.get(f"M{M}_K{K}_B{B}")
                if ex_log:
                    lead = 0
                    for cap, st in ex_log:
                        if st != "unsat":
                            break
                        lead += 1
                    lb["max_meet"] = max(lb["max_meet"], lead + 1)
                lbl = [lb[f] for f in SCORE_FIELDS]
                rb = rule_best(M, K, B)
                rdraw = rule_draw(M, K, B, rb["d"], rb["pi"])
                rs = evaluate(rdraw)
                rex = rule_exclusion(M, K, rb["d"], rb["pi"])
                cand = [("rule", tuple(rs["score"]), rdraw, rs)]
                p = os.path.join(HERE, "results", "opt", f"M{M}_K{K}_B{B}.json")
                if os.path.exists(p):
                    o = json.load(open(p))
                    od = relabel(o["draw"])
                    od0 = [[[x - 1 for x in pr] for pr in blk] for blk in od]
                    os_ = evaluate(od0)
                    cand.append(("draw", tuple(os_["score"]), od0, os_))
                cand.sort(key=lambda c: c[1])   # stable: rule first on ties
                kind, score, draw, r = cand[0]
                proven = 0
                for v, l in zip(score, lbl):
                    if v != l:
                        break
                    proven += 1
                # unconstrained comparison: best mixing found without the
                # lane-pair balance constraint (results/opt_free)
                free_mix = tuple(score[1:NMIX])
                pf_ = os.path.join(HERE, "results", "opt_free", f"M{M}_K{K}_B{B}.json")
                if os.path.exists(pf_):
                    fo = json.load(open(pf_))
                    fs = evaluate(fo["draw"])["score"]
                    free_mix = min(free_mix, tuple(fs[1:NMIX]))
                nzd, nzpi = baseline_rules(M, K)["nz"]
                nz = evaluate(rule_draw(M, K, B, nzd, nzpi))
                s = dict(id=f"M{M}_K{K}_B{B}", M=M, K=K, B=B,
                         games_g1=B, games_g2=[2 * B - 1, 2 * B],
                         type=kind,
                         score={f: (-r["min_meet"] if f == "neg_min_meet" else r[f]) for f in SCORE_FIELDS},
                         extra=dict(min_meet=r["min_meet"], never_met=r["never_met"],
                                    min_distinct_followed=r["min_distinct_followed"],
                                    min_distinct_followers=r["min_distinct_followers"]),
                         lower_bound=lbl, proven_fields=proven,
                         optimal=proven == len(SCORE_FIELDS),
                         mixing_optimal=proven >= NMIX,
                         sgp_rounds_known=known, sgp_rounds_max=SGP[(M, K)][1],
                         rule=None,
                         best_rule=dict(d=[x % M for x in rb["d"]], pi=rb["pi"],
                                        words=describe_rule(M, K, rb["d"], rb["pi"]),
                                        score=list(rs["score"]),
                                        never_meet_ever=rex["never_meet"],
                                        ties_best=tuple(rs["score"]) == score,
                                        ties_best_mixing=tuple(rs["score"])[:NMIX] == score[:NMIX]),
                         nz_score=list(nz["score"]),
                         unconstrained_mixing=list(free_mix),
                         balance_costs_mixing=free_mix < tuple(score[1:NMIX]),
                         draw=[[[x + 1 for x in pr] for pr in blk] for blk in draw])
                if kind == "rule":
                    s["rule"] = dict(d=[x % M for x in rb["d"]], pi=rb["pi"],
                                     words=describe_rule(M, K, rb["d"], rb["pi"]),
                                     never_meet_ever=rex["never_meet"])
                out.append(s)
                summary.append({k: v for k, v in s.items() if k != "draw"})
            summary.append(dict(id=f"M{M}_K{K}_universal", M=M, K=K, universal_rule=dict(
                d=uni["d"], pi=uni["pi"], optimal_for_B_up_to=uni["prefix"],
                words=describe_rule(M, K, uni["d"], uni["pi"]))))
    doc = dict(
        description="Recommended qualifying lane movements. M pairs, K bowlers per pair, "
                    "B blocks (bowlers move between blocks). draw[block][pair] lists bowler "
                    "numbers in bowling order (1st = left lane start, 2nd = right, ...). "
                    "Bowlers are numbered by their block-1 seat: (pair-1)*K + position.",
        score_fields=list(SCORE_FIELDS),
        follow_convention="lane cycle 1,3,5,..,2,4,..: each bowler bowls straight after "
                          "the previous bowler in this cycle, on both lanes",
        rule_convention="after each block the bowler in (pair p, position t) moves to "
                        "(pair p + d[t] mod M, position pi[t]+1); t, pi 0-based",
        schemes=out)
    json.dump(doc, open(os.path.join(HERE, "schemes.json"), "w"), separators=(",", ":"))
    json.dump(summary, open(os.path.join(HERE, "results", "summary.json"), "w"), indent=0)
    print(len(out), "schemes")


if __name__ == "__main__":
    main()
