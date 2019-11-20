#!/bin/bash
basename=/usr/people/out/Documents/Magnetic_field/station_results/29-10-2003/interpolation

for item in $basename/*.csv; do
awk '{t=$1;$1=$2;$2=t;print}' $item > $item.out
mv $item.out $item
done
