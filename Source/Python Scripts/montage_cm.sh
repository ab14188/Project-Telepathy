#!/bin/bash
echo "Creating confusion matrices montage"
i=0
mkdir tmp
for d in ./user_study/results/*
do 
	echo $d
	for file in $d$"/CM2/*"
	do 
		echo $file
		montage $file -geometry 800x600 -tile 2x1 tmp/tmp"$i".pdf
		let "i += 1"
	done
done

convert tmp/* cm_montage3.pdf

rm -r tmp