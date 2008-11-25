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

SUBARCH=$1
if [ "$#" = "3" ]
then
	CURDATE=$3
else
	CURDATE=`date +%Y.%m.%d`
fi

if [ "$#" = "2" ] || [ "$#" = "3" ]
then
	BUILDTYPE=$2
else
	BUILDTYPE=full
fi

CONTROL=`metro -k path/mirror/control target/subarch: $SUBARCH`

if [ ! -d "$CONTROL" ]
then
	die "Control directory $CONTROL (from 'metro -k path/mirror/control target/subarch: $SUBARCH') does not exist."
fi

do_everything() {
	echo "Starting..."
	if [ "$BUILDTYPE" = "full" ]
	then
		local builds="snapshot stage1 stage2 stage3"
	elif [ "$BUILDTYPE" = "quick" ]
	then
		local builds="snapshot stage3-quick"
	elif [ "$BUILDTYPE" = "freshen" ]
	then
		local builds="snapshot stage3-freshen"
	else
		die "Build type \"$BUILDTYPE\" not recognized."
	fi
	[ "${SUBARCH:0:1}" = "~" ] && builds="$builds openvz"
	for x in $builds 
	do
		metro target/version: $CURDATE target: gentoo/$x target/subarch: $SUBARCH || die "$x fail: metro target/version: $CURDATE target: gentoo/$x target/subarch: $SUBARCH"
		if [ "${x:0:6}" = "stage3" ]
		then
			# Did we just complete a stage3* build? OK, then
			# record a successful build so we use our new stage3 as a seed stage3 for next time.
			echo $CURDATE > $CONTROL/lastdate
			echo $SUBARCH > $CONTROL/subarch
		fi
	done
}

do_everything
