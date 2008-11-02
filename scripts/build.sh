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

if [ $# -lt 1 ] || [ $# -gt 2 ]
then
	do_help
	die "This script requires one or two arguments"
fi

SUBARCH=$1
if [ "$#" = "2" ]
then
	CURDATE=$2
else
	CURDATE=`date +%Y.%m.%d`
fi

CONTROL=`metro -k path/mirror/control target/subarch: $SUBARCH`

if [ ! -d "$CONTROL" ]
then
	die "Control directory $CONTROL (from 'metro -k path/mirror/control target/subarch: $SUBARCH') does not exist."
fi

do_everything() {
	echo "Starting..."
	local builds="snapshot stage1 stage2 stage3"
	[ "${SUBARCH:0:1}" = "~" ] && builds="$builds openvz"
	for x in $builds 
	do
		metro target/version: $CURDATE target: gentoo/$x target/subarch: $SUBARCH || die "$x fail: metro target/version: $CURDATE target: gentoo/$x target/subarch: $SUBARCH"
		if [ "$x" = "stage3" ]
		then
			#record successful build for next time
			echo $CURDATE > $CONTROL/lastdate
			echo $SUBARCH > $CONTROL/subarch
		fi
	done
}

do_everything
