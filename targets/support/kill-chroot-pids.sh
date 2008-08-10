#!/bin/bash
# Script to kill processes found running in the chroot.

if [ "${clst_chroot_path}" == "/" ]
then
	echo "Aborting .... clst_chroot_path is set to /"
	echo "This is very dangerous"
	exit 1
fi

if [ "${clst_chroot_path}" == "" ]
then
	echo "Aborting .... clst_chroot_path is NOT set"
	echo "This is very dangerous"
	exit 1
fi

j=0
declare -a pids
# Get files and dirs in /proc
for i in `ls /proc`
do
	# Test for directories
	if [ -d /proc/$i ]
	then
	# Search for exe containing string inside ${clst_chroot_path}
	ls -la --color=never /proc/$i 2>&1 |grep exe|grep ${clst_chroot_path} > /dev/null

	# If found
	if [ $? == 0 ]
	then
		# Assign the pid into the pids array
		pids[$j]=$i
		j=$(($j+1))
	fi
	fi
done

if [ ${j} -gt 0 ]
then
	echo
	echo "Killing process(es)"
	echo "pid: process name"
	for pid in ${pids[@]} 
	do 
		P_NAME=$(ls -la --color=never /proc/${pid} 2>&1 |grep exe|grep ${clst_chroot_path}|awk '{print $11}')
		echo ${pid}: ${P_NAME}
	done
	echo 
	echo "Press Ctrl-C within 10 seconds to abort"
	
	sleep 10

	for pid in ${pids[@]} 
	do
		kill -9 ${pid}
	done

	# Small sleep here to give the process(es) a chance to die before running unbind again.
	sleep 5

fi
