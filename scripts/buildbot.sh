#!/bin/bash
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
	if [ "$build" = "funtoo-current" ]; then
		if [ "$subarch" = "corei7" ]; then
			buildtype="$buildtype+openvz"
		fi
		if [ "$subarch" = "core2_64" ]; then
			buildtype="$buildtype+openvz"
		fi
		if [ "$subarch" = "generic_64" ]; then
			buildtype="$buildtype+openvz"
		fi
	fi
	if [ "$build" != "" ] && [ "$subarch" != "" ] && [ "$buildtype" != "" ]; then
		echo "Building $build $subarch $buildtype"
		exec /root/git/metro/scripts/ezbuild.sh $build $subarch $buildtype
	else
		echo "Couldn't determine build, subarch and build type. Exiting."
		exit 1
	fi
}
( cd /root/git/metro; git pull )
export METRO_BUILDS="funtoo-current funtoo-stable funtoo-experimental"
export STALE_DAYS=3
cd /var/tmp
a=$(/root/git/metro/scripts/buildrepo nextbuild)
if [ $? -eq 1 ]; then
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
