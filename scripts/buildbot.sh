#!/bin/bash

if [ "$1" == "--pretend" ]; then
	PRETEND=yes
else
	PRETEND=no
fi

kcfile="/root/.keychain/$(hostname)-sh"
[ -e "$kcfile" ] && . "$kcfile"
dobuild() {
	local build=$1
	local subarch=$2
	# buildrepo returns True for this argument if last build had a stage1 built too (non-freshen), otherwise False
	local full=$3
	local buildtype=full
	if [ "$full" = "True" ]; then
		buildtype="freshen"
	fi
	if [ "$subarch" = "corei7" ]; then
		buildtype="$buildtype+openvz"
	fi
	if [ "$subarch" = "corei7-pure64" ]; then
		buildtype="$buildtype+openvz"
	fi	
	if [ "$subarch" = "core2_64" ]; then
		buildtype="$buildtype+openvz"
	fi
	if [ "$subarch" = "generic_64" ]; then
		buildtype="$buildtype+openvz"
	fi
	if [ "$subarch" = "generic64-pure64" ]; then
		buildtype="$buildtype+openvz"
	fi	
	if [ "$subarch" = "generic_32" ]; then
		buildtype="$buildtype+openvz"
	fi
	if [ "$subarch" = "core2_32" ]; then
		buildtype="$buildtype+openvz"
	fi
	if [ "$build" != "" ] && [ "$subarch" != "" ] && [ "$buildtype" != "" ]; then
		echo "Building $build $subarch $buildtype"
		if [ "$PRETEND" = "yes" ]; then
			echo /root/git/metro/scripts/ezbuild.sh $build $subarch $buildtype
		else
			/root/git/metro/scripts/ezbuild.sh $build $subarch $buildtype
			if [ $? -ne 0 ]; then
				return $EXIT_CODE_ON_SUCCESS
			else
				return $EXIT_CODE_ON_FAL
			fi
		fi
	else
		echo "Couldn't determine build, subarch and build type. Exiting."
		exit 1
	fi
}
( cd /root/git/metro; git pull )
export METRO_BUILDS="funtoo-current funtoo-stable funtoo-experimental"
export STALE_DAYS=5
export SKIP_SUBARCH="amd64-k10"
# Allow tweaking for cron to get the emails you want. These values will be returned only
# after a non-pretend dobuild() run.
export EXIT_CODE_ON_SUCCESS=1
export EXIT_CODE_ON_FAIL=2
cd /var/tmp
a=$(/root/git/metro/scripts/buildrepo nextbuild)
if [ "$PRETEND" = "yes" ]; then
	echo $a
fi
if [ "$a" = "" ]; then
	echo "Builds are current."
	# we are current
	exit 0
elif [ $? -eq 2 ]; then
	# error
	echo "buildrepo error: (re-doing to get full output):"
	/root/git/metro/scripts/buildrepo nextbuild
	exit 1
fi
# otherwise, build what needs to be built:
dobuild $a
