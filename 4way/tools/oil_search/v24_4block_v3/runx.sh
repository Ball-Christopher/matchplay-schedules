#!/bin/bash
# runx.sh sigvariant dxfile part nparts timeout : A-search for every nparts-th candidate X
i=0
while read lo hi rest; do
  if [ $((i % $4)) -eq $3 ]; then
    r=$(timeout $5 ./asearch out/pool2.mask out/pool2.sig$1 $lo $hi 20 | tr '\n' '~')
    echo "X $i $lo $hi $rest => $r"
  fi
  i=$((i+1))
done < $2
