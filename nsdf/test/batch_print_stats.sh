#!/bin/bash
# Print the stats from all profiling files
dialects=( 1d vlen nan )
compression=( compressed uncompressed )
for dl in "${dialects[@]}"; do
    echo "==========================="
    echo "Dialect: $dl"
    for cmp in "${compression[@]}"; do
	echo -e "\t$cmp"
	echo "==========================="
	for ii in $(seq 0 9); do
	    echo -e "\t\t$ii"
	    fname="$dl"_"$cmp"_"$ii".prof
	    echo "Processing $fname"
	    python print_stats.py $fname | awk 'BEGIN {sum=0;} /NSDFWriter\.py:.*add_/  {sum+=$4; print $4} END {print "SUM:", sum;}'
	done
    done
done
