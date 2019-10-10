#!/bin/bash
source /etc/profile
#preserve group permissions:
umask 002
SCRIPT_DIR=$(readlink -f $(dirname ${BASH_SOURCE[0]}))
cd $SCRIPT_DIR
if [ ! -e ./buildrepo ]; then
	echo "can't find buildrepo. Path is " `cwd`
	exit 1
fi
a=$(./buildrepo nextbuild)
if [ $? -eq 2 ]; then
	# error
	echo "buildrepo error: (re-doing to get full output):"
	./buildrepo nextbuild
	exit 1
fi
if [ "$a" = "" ]; then
	echo "Builds are current."
	# we are current
	exit 0
else
	# evaluate output of buildrepo to get things defined as env vars:
	eval $a
	if [ -z "$release" ]; then
		echo "release not defined. Call to buildrepo probably failed. Exiting."
		exit 1
	fi
	if [ "$1" == "--pretend" ]; then
		cmd="echo ../metro"
	else
		cmd="../metro"
	fi
	echo -n "Building $release for $subarch ($target) with date $nextdate"
	if [ -n "$extras" ]; then
		# convert into metro argument:
		extras="multi/extras: $extras"
		echo " (extras: $extras)"
	else
		echo
	fi
	$cmd -d multi: yes target/build: $release target/arch_desc: $arch_desc target/subarch: $subarch target/version: $nextdate multi/mode: $target $extras
	exit $?
fi
