#!/bin/bash
cat cherokee.access | head -n 1 | cut -f4,5 -d" "
cat cherokee.access | tail -n 1 | cut -f4,5 -d" "

# Set $build to the build you want stats on, or set to "" for all builds (total)

build="funtoo"

for sub in i686 core2 amd64 x86 core2_32 pentium4 opteron athlon-xp phenom opteron_32
do
	for stage in stage1 stage2 stage3
	do
		if [ "$build" = "" ]
		then
			grepme="${stage}-${sub}"
		else
			grepme="${build}/${sub}/${stage}-${sub}"
		fi
		num=`cat cherokee.access | cut -f1,6,7 -d" " | grep "${grepme}" | uniq | wc -l`
		echo "$num $sub $stage "
	done
done
