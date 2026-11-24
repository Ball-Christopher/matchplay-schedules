"""v24 0-10-1: the 2019 archive weeks, re-laned and re-positioned."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import build, HYB
d = json.load(open(os.path.join(HYB, 'files', 'v24_archive2019.json')))
weeks = [[g for g in wk if g] for wk in d['weeks']]
build(24, weeks, "2019 archive weeks (1x4-way + 10x3-way, a 3-RGDD of type 4^6) reused unchanged; lane pairs re-assigned by annealing, positions by de Werra equitable colouring (tools/positions.py)", "v24_0-10-1.json", n=8)
