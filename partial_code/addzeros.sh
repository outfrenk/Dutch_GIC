#!/bin/bash
basename=/usr/people/out/Documents/Magnetic_field/station_results/29-10-2003/interpolation

for item in $basename/minlon_?.png; do
item2=${item:0:89}000${item:89:100};
mv $item $item2
done

for item in $basename/minlon_??.png; do
item2=${item:0:89}00${item:89:100};
mv $item $item2
done

for item in $basename/minlon_???.png; do
item2=${item:0:89}0${item:89:100};
mv $item $item2
done
