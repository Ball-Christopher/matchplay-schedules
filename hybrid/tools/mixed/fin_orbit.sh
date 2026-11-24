#!/bin/bash
# fin_orbit.sh raw/NAME.json "orbit description": lane pairs = most groups in a week, no wrapping, then positions (lanes_anneal.py)
raw=$1; desc=$2
n=$(python3 -c "import json;d=json.load(open('$raw'));print(max(len(w) for w in d['weeks']))")
python3 "$(dirname "$0")/lanes_anneal.py" "$raw" "$desc; orbit annealing (tools/mixed/oanneal.c, batch.py); lane pairs by annealing (tools/mixed/lanes_anneal.py), positions by z3." --n $n --secs 60 --allow-off
