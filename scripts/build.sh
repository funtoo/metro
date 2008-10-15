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

OUTDIR=`metro -k path/mirror`
if [ ! -d $OUTDIR ]
then
	die "Mirror directory $OUTDIR (from 'metro -k path/mirro') does not exist."
fi

SUBARCH=$1
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
	#metro -k /usr/lib/metro/etc/USER-snapshot-funtoo.spec target/version: $CURDATE
	echo "Starting..."
	if [ "$UNSTABLE" = "yes" ]
	then
		metro -d /usr/lib/metro/etc/USER-snapshot-funtoo.conf target/version: $CURDATE || die "snapshot fail"
	else
		metro -d /usr/lib/metro/etc/USER-snapshot.conf target/version: $CURDATE || die "snapshot fail"
	fi
	metro /usr/lib/metro/etc/USER-stage1.conf target/version: $CURDATE target/subarch: $SUBARCH || die "stage1 fail"
	metro /usr/lib/metro/etc/USER-stage2.conf target/version: $CURDATE target/subarch: $SUBARCH || die "stage2 fail"
	metro /usr/lib/metro/etc/USER-stage3.conf target/version: $CURDATE target/subarch: $SUBARCH || die "stage3 fail"
	# update what we will build against next time:
	echo $CURDATE > /home/mirror/linux/$SUBARCH/.control/lastdate
	echo $SUBARCH > /home/mirror/linux/$SUBARCH/.control/subarch
}

do_everything
