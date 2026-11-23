#!/bin/bash
for n in $(seq $1 $3 $2); do [ -f out/eq_$n.txt ] && ./lanes_eq out/eq_$n.txt out/eqlanes_$n.txt 3 20 0.7 0.1 30 0; done
