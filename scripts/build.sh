#!/bin/bash

# If we are running from fcron, we'll have a clean environment and thus won't have proxy settings. So let's make sure we have a good Gentoo environment...
source /etc/profile

die() {
	echo $*
	exit 1
}

if [ ! -e /usr/bin/metro ]
then
	die "Metro is required for build.sh to run"
fi

BUILD=$1
SUBARCH=$2
CONTROL=`metro -k path/mirror/control build/type: $BUILD build/subarch: $SUBARCH`
if [ ! -d $CONTROL ]
then
	die "Control directory $CONTROL (from 'metro -k path/mirror/control target/subarch: $SUBARCH') does not exist."
fi

if [ "$#" = "2" ]
then
	CURDATE=$2
else
	CURDATE=`date +%Y.%m.%d`
fi

do_help() {
	cat << EOF

  Metro Automation Engine Script
  by Daniel Robbins (drobbins@funtoo.org)

  Usage: $0 arch [version]
  Example: $0 amd64

EOF
}

if [ "${SUBARCH:0:1}" = "~" ]
then
	UNSTABLE="yes"
fi

if [ $# -lt 1 ] || [ $# -gt 2 ]
then
	do_help
	die "This script requires one or two arguments"
fi

do_everything() {
	echo "Starting..."
	metro build/type: $BUILD target/version: $CURDATE target: $x || die "$x fail"
	for x in stage1 stage2 stage3
	do
		metro build/type: $BUILD target/version: $CURDATE target: $x build/subarch: $SUBARCH || die "$x fail"
	done
	# update what we will build against next time:
	echo $CURDATE > $CONTROL/lastdate
	echo $SUBARCH > $CONTROL/subarch
	if [ "$UNSTABLE" = "yes" ]
	then
		metro build/type: $BUILD target/version $CURDATE target: openvz build/subarch: $SUBARCH || die "openvz fail"
	fi
}

do_everything
