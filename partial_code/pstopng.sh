#!/bin/bash
basename=/usr/people/out/Documents/Magnetic_field/station_results/29-10-2003/interpolation

for item in $basename/minlon_*.ps; do
item=${item%.ps};
echo $item
convert -density 300 $item.ps $item.png;
done
