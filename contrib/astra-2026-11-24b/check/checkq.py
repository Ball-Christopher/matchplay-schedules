import json,glob,os,sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'../../../qualifying'))
from model import evaluate
IN=sys.argv[1]
S={e['id']:e for e in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../../../qualifying/schemes.json')))['schemes']}
F=['pair_spread','max_meet','max_follow','repeats','follow_repeats']
for f in sorted(glob.glob(IN+'/qualifying/*.json'),key=lambda p:[int(x[1:]) for x in os.path.basename(p)[:-5].split('_')]):
    a=json.load(open(f)); M,K,B=a['M'],a['K'],a['B']
    draw=[[[x-1 for x in g] for g in blk] for blk in a['draw']]
    assert len(draw)==B and all(len(b)==M and all(len(g)==K for g in b) for b in draw)
    r=evaluate(draw); minspread=0 if B%M==0 else 1
    old=S.get(a['id'],{}).get('score',{})
    claim=(a['score']['max_meet'],a['score']['max_follow'])
    got=(r['max_meet'],r['max_follow'])
    flag='' if (got==claim and r['pair_spread']==minspread) else ' <<MISMATCH'
    lb=S.get(a['id'],{}).get('lower_bound')
    print(f"{a['id']:12} spread {r['pair_spread']}(min {minspread}) claim {claim} got {got} repeats {r['repeats']}/{r['follow_repeats']} | repo {tuple(old.get(k) for k in F)} lb {lb[:3] if lb else None}{flag}")
