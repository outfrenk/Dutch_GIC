#!/bin/bash
basename=/usr/people/out/Documents/Magnetic_field/station_results/29-10-2003/interpolation
for item in $basename/*.csv; do
awk '{t=$3;$3=$4;$4=t;print}' $item > $item.Y
done
