#!/bin/bash
# lanes_all.sh first last : run lanes SA on designs first..last sequentially
for n in $(seq $1 $2); do [ -f out/design_$n.txt ] && ./lanes out/design_$n.txt out/lanesC_$n.txt 7 150 0.45 0.12 3; done
