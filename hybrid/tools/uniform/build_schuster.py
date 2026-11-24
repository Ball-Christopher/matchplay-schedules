"""v24 0-7-3 and 0-4-5 from the explicit URD({3,4};24) designs in E. Schuster,
"Uniformly resolvable designs with index one, block sizes three and four - with three or
five parallel classes of block size four", Discrete Math. 309 (2009) 2452-2465,
Examples A.6 (r4 = 3) and A.7 (r4 = 5), transcribed in out/schuster2009_A6.json / _A7.json."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import finish
HERE = os.path.dirname(os.path.abspath(__file__))
REF = 'E. Schuster, Discrete Math. 309 (2009) 2452-2465, Example A.%s (URD({3,4};24) with r4 = %d, found there with the program DESIGN)'
if __name__ == '__main__':
    secs = float(sys.argv[1]) if len(sys.argv) > 1 else 60
    for ex, r4, fn in (('6', 3, 'v24_0-7-3.json'), ('7', 5, 'v24_0-4-5.json')):
        W = json.load(open(os.path.join(HERE, 'out', f'schuster2009_A{ex}.json')))
        finish(24, W, fn, REF % (ex, r4), seconds=secs)
