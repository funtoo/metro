#!/bin/bash

# If we are running from fcron, we'll have a clean environment and thus won't have proxy settings. So let's make sure we have a good Gentoo environment...
source /etc/profile

die() {
	echo $*
	exit 1
}

do_help() {
	cat << EOF

  Metro Automation Engine Script
  by Daniel Robbins (drobbins@funtoo.org)

  Usage: $0 arch [version]
  Example: $0 amd64

EOF
}

if [ ! -e /usr/bin/metro ]
then
	die "Metro is required for build.sh to run"
fi

if [ $# -lt 1 ] || [ $# -gt 3 ]
then
	do_help
	die "This script requires one, two or three arguments"
fi

if [ "$#" = "2" ] || [ "$#" = "3" ]
then
	BUILDTYPE=$2
else
	BUILDTYPE=full
fi

SUBARCH=$1
if [ "$#" = "3" ]
then
	CURDATE=$3
else
	CURDATE=`date +%Y.%m.%d`
fi
if [ "$BUILDTYPE" = "full" ]
then
	builds="stage1 stage2 stage3"
elif [ "$BUILDTYPE" = "quick" ]
then
	builds="stage3-quick"
elif [ "$BUILDTYPE" = "freshen" ]
then
	builds="stage3-freshen"
else
	die "Build type \"$BUILDTYPE\" not recognized."
fi
	if [ "${SUBARCH:0:1}" = "~" ] 
then
	# for funtoo builds, we create a "live" git snapshot (full repo) and we also build an openvz template
	builds="git-snapshot $builds openvz"
	mb="funtoo"
else
	# for stable builds, we create a traditional portage snapshot that is just a tarball of the physical files
	builds="snapshot $builds"
	mb="gentoo"
fi

MAINARGS="metro/build: $mb target/subarch: $SUBARCH target/version: $CURDATE"
CONTROL=`metro -k path/mirror/control $MAINARGS`

if [ ! -d "$CONTROL" ]
then
	die "Control directory $CONTROL (from 'metro -k path/mirror/control $MAINARGS') does not exist."
fi

do_everything() {
	echo "Starting..."
	for x in $builds 
	do
		metro $MAINARGS target: $x || die "$x fail: metro $MAINARGS target: $x"
		if [ "${x:0:6}" = "stage3" ]
		then
			# Did we just complete a stage3* build? OK, then
			# record a successful build so we use our new stage3 as a seed stage3 for next time.
			echo $CURDATE > $CONTROL/lastdate
			echo $SUBARCH > $CONTROL/subarch
			CURRENT=`metro -k path/mirror/stage3/current $MAINARGS target: $x`
			TARGET=`metro -k path/mirror/stage3/current/dest $MAINARGS target: $x`
			# update current symlink
			rm -f "$CURRENT"
			ln -s "$TARGET" "$CURRENT"
		fi
	done
}

do_everything
