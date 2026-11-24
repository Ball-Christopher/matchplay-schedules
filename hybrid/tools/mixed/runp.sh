#!/bin/bash
# runp.sh prog outfile secs jobs args... : run prog with seeds 1..jobs in parallel; keep first success
prog=$1; out=$2; secs=$3; jobs=$4; shift 4
tmp=$(mktemp -d)
for s in $(seq 1 $jobs); do ( $prog ${@//SEED/$s} > $tmp/$s.out 2>$tmp/$s.err && cp $tmp/$s.out $out.tmp$s ) & done
wait
f=$(ls $out.tmp* 2>/dev/null | head -1); if [ -n "$f" ]; then mv $f $out; rm -f $out.tmp*; echo "found $out"; else echo "none for $out"; cat $tmp/*.err | sort | uniq -c | head; fi
rm -rf $tmp
