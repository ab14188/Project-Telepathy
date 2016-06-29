#!/bin/bash

echo "Creating montage"

i=0
mkdir tmp

for d in ./user_study/results/test2/Graphs/*
do
	echo $d
	montage $d/* -geometry 800x600 -tile 10x1 tmp/tmp"$i".pdf

	let "i += 1"

done
convert tmp/* montage.pdf
	
rm -r tmp