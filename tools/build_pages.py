#!/usr/bin/env python3
"""Build the web pages and the README catalogue from the schedule files.

Reads every 3way/v*.json and 4way/v*.json, recomputes the balance figures from
the weeks alone (as verify.py does), and writes:

  docs/schedules.json   every schedule with its figures and notes
  docs/index.html       the schedule picker (site/index.html with the data inlined)
  docs/methods.html     METHODS.md as HTML (needs pandoc)
  README.md             the catalogue table between the catalogue markers

Usage: python3 tools/build_pages.py [--site DIR]
  --site DIR   also copy the three docs/ files into DIR (for example the
               website's schedules/ folder)
"""
import argparse, html, itertools, json, re, shutil, subprocess, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KINDS = {"": "single", "_vacant": "vacant", "_x2": "x2", "_oil": "oil", "_oil_x2": "oilx2"}
SUFFIX = {"single": "", "vacant": "-vacant", "x2": "-x2", "oil": "-oil", "oilx2": "-oil-x2"}
LABEL = {
    "single": "One round",
    "vacant": "One round, one slot empty",
    "x2": "Two rounds",
    "oil": "One round in oil-pattern blocks",
    "oilx2": "Two rounds in oil-pattern blocks",
}

# Hand-written context the figures alone can't give.  Keyed by schedule ID.
NOTES = {
    "3w15": ["Exact lane balance is impossible for 15 bowlers in threes: every one of the 7 "
             "possible Kirkman designs was checked, and a published result agrees. The two-round schedule 3w15-x2 is exact."],
    "4w12": ["Exact lane balance is impossible for 12 bowlers in fours over 11 weeks (a published result: "
             "no GBTD(4,3) exists), so 1 bowler off is the best possible. The two-round schedule 4w12-x2 is exact."],
    "4w16": ["Exact lane balance is impossible for 16 bowlers in fours over 5 weeks (the affine-plane "
             "argument in the methods). The two-round schedule 4w16-x2 is exact."],
    "4w16-vacant": ["Exact lane balance is impossible here too; 3 bowlers off is the best possible."],
    "4w12-oil": ["With 12 bowlers in fours, any two weeks share a couple, so some couples must meet "
                 "twice on one pattern. 27 extra meetings is the minimum for 4 patterns (40 for 3), "
                 "proven by checking all five possible designs."],
    "4w24-oil": ["4 patterns, the fewest possible; every couple meets on 3 different patterns."],
    "4w36-oil": ["It takes 11 patterns; the lower bound is 4. A natural 4-pattern construction is proven impossible, "
                 "and whether 4 is possible at all is open."],
    "4w40": ["The first known 40-bowler schedule in fours with exact lane balance (built from the geometry PG(3,3))."],
    "3w18-oil-x2": ["Round 1 is the one-round oil schedule 3w18-oil unchanged; 5 patterns over the two rounds is the fewest possible."],
    "3w12": ["The oil-pattern split (4, 3 and 4 weeks) is built in, and 3 patterns is the fewest possible."],
}
ANCHOR = {  # which METHODS.md section explains the hard part of each schedule
    "single": "2-pair-balance-constructing-the-designs",
    "vacant": "5-vacancy-n1-files",
    "x2": "6-two-round-files",
    "oil": "10-oil-pattern-blocks",
    "oilx2": "10-oil-pattern-blocks",
}


def analyse(path):
    d = json.loads(path.read_text())
    k, v, W = d["group"], d["players"], d["weeks"]
    kind = KINDS[re.match(r"v\d+(.*)", path.stem).group(1)]
    sid = f"{k}w{v}{SUFFIX[kind]}"
    vac = d.get("vacant")
    real = [p for p in range(1, v + 1) if p != vac]
    n, r = v // k, len(W)
    blocks = d.get("blocks") or d.get("oil_blocks")
    meet, lane, pos, prefix = Counter(), Counter(), Counter(), []
    couples = list(itertools.combinations(real, 2))
    week_groups = []
    for w in W:
        groups = [w[g * k:(g + 1) * k] for g in range(n)]
        week_groups.append(frozenset(frozenset(g) for g in groups))
        for g, grp in enumerate(groups):
            for q, p in enumerate(grp):
                lane[p, g] += 1
                pos[p, q] += 1
            for a, b in itertools.combinations(sorted(grp), 2):
                meet[a, b] += 1
        vals = [meet[c] for c in couples]
        prefix.append(max(vals) - min(vals))
    lam = sorted({meet[c] for c in couples})
    assert len(lam) == 1, (path, lam)
    lo, hi = r // n, -(-r // n)
    off = {p: [lane[p, g] for g in range(n)] for p in real
           if any(not lo <= lane[p, g] <= hi for g in range(n))}
    plo, phi = r // k, -(-r // k)
    assert all(plo <= pos[p, q] <= phi for p in real for q in range(k)), path

    e = {
        "id": sid, "file": f"{path.parent.name}/{path.stem}", "k": k, "slots": v,
        "bowlers": len(real), "kind": kind, "label": LABEL[kind], "weeks": W,
        "lanes": n, "lambda": lam[0], "rounds": 2 if kind in ("x2", "oilx2") else 1,
        "vacant": vac, "blocks": blocks, "lane_range": [lo, hi], "lane_off": off,
        "position_range": [plo, phi], "prefix_spread": prefix,
        "worst_prefix": max(prefix[:-1]) if r > 1 else 0,
        "method": d.get("method", ""), "notes": [], "methods_anchor": ANCHOR[kind],
    }
    # -- notes worked out from the weeks ------------------------------------
    notes = e["notes"]
    if blocks:
        cuts = list(itertools.accumulate(blocks))
        rep, start = 0, 0
        for end in cuts:
            m = Counter()
            for w in W[start:end]:
                for g in range(n):
                    for c in itertools.combinations(sorted(w[g * k:(g + 1) * k]), 2):
                        m[c] += 1
            rep += sum(x - 1 for c, x in m.items() if x > 1 and vac not in c)
            start = end
        e["block_repeats"] = rep
    distinct = len(set(week_groups))
    e["distinct_weeks"] = distinct
    if distinct < r:
        dup = [i + 1 for i, g in enumerate(week_groups) if g in week_groups[:i]]
        notes.append(f"{r - distinct} week(s) repeat an earlier week's groups exactly "
                     f"(week {', '.join(map(str, dup))}). The lane pairs differ, so balance is unaffected.")
    if kind in ("x2", "oilx2"):
        half = r // 2
        first = {g for wk in W[:half] for g in (frozenset(wk[i * k:(i + 1) * k]) for i in range(n))}
        again = sum(frozenset(wk[i * k:(i + 1) * k]) in first for wk in W[half:] for i in range(n))
        e["repeated_groups"] = again
        if again:
            notes.append(f"{again} group(s) from round 1 bowl together again in round 2. Every couple "
                         f"still meets exactly {lam[0]} times.")
    if vac:
        vl = {g for w in W for g in range(n) if vac in w[g * k:(g + 1) * k]}
        if len(vl) == 1:
            notes.append(f"The short group (the empty slot) is on lane pair {vl.pop() + 1} every week.")
    notes.extend(NOTES.get(sid, []))
    return e


def catalogue(entries):
    rows = ["| ID | Bowlers | Weeks | Couples meet | Lane pairs | Oil patterns | File |",
            "|---|---|---|---|---|---|---|"]
    for e in entries:
        lanes = "exact" if not e["lane_off"] else f"{len(e['lane_off'])} bowler(s) off"
        oil = "+".join(map(str, e["blocks"])) if e["blocks"] else ""
        if e["blocks"] and e.get("block_repeats"):
            oil += f" ({e['block_repeats']} repeats)"
        bowl = f"{e['bowlers']}" + (f" (slot {e['vacant']} empty)" if e["vacant"] else "")
        rows.append(f"| `{e['id']}` | {bowl} | {len(e['weeks'])} | {e['lambda']}× | {lanes} | {oil} "
                    f"| [{e['file']}.toml]({e['file']}.toml) |")
    return "\n".join(rows)


def methods_html():
    body = subprocess.run(["pandoc", "-f", "gfm", "-t", "html", str(ROOT / "METHODS.md")],
                          check=True, capture_output=True, text=True).stdout
    tpl = (ROOT / "site" / "methods.html.in").read_text()
    return tpl.replace("<!--BODY-->", body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", type=Path)
    a = ap.parse_args()
    order = {"single": 0, "vacant": 1, "x2": 2, "oil": 3, "oilx2": 4}
    entries = sorted((analyse(p) for f in ("3way", "4way") for p in (ROOT / f).glob("v*.json")),
                     key=lambda e: (e["k"], e["slots"], order[e["kind"]]))
    docs = ROOT / "docs"
    docs.mkdir(exist_ok=True)
    data = json.dumps(entries, separators=(",", ":"))
    (docs / "schedules.json").write_text(data)
    page = (ROOT / "site" / "index.html.in").read_text()
    page = page.replace("/*DATA*/null", data.replace("</", "<\\/"))
    (docs / "index.html").write_text(page)
    (docs / "methods.html").write_text(methods_html())
    readme = (ROOT / "README.md").read_text()
    readme = re.sub(r"(<!-- catalogue:start -->).*?(<!-- catalogue:end -->)",
                    lambda m: m.group(1) + "\n" + catalogue(entries) + "\n" + m.group(2), readme, flags=re.S)
    (ROOT / "README.md").write_text(readme)
    if a.site:
        a.site.mkdir(parents=True, exist_ok=True)
        for f in ("index.html", "methods.html", "schedules.json"):
            shutil.copy2(docs / f, a.site / f)
    print(f"{len(entries)} schedules -> docs/" + (f" and {a.site}" if a.site else ""))


if __name__ == "__main__":
    main()
