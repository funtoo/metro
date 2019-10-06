#!/bin/bash

# If we are running from fcron, we'll have a clean environment and thus won't
# have proxy settings. So let's make sure we have a good Gentoo environment...

source /etc/profile
SCRIPT_DIR=$(readlink -f $(dirname ${BASH_SOURCE[0]}))
cd $SCRIPT_DIR
die() {
	echo $*
	exit 1
}

run() {
	echo Running $*
	$*
	return $?
}

do_help() {
	cat << EOF

  Metro Automation Engine Script
  by Daniel Robbins (drobbins@funtoo.org)

  Usage: $0 build arch subarch [ full|freshen|quick [date] ]
  Examples:
  	# $0 1.3-release-std x86-64bit generic_64
	# $0 1.3-release-std x86-32bit core2_32 freshen
EOF
}

if [ $# -lt 2 ] || [ $# -gt 5 ]
then
	do_help
	die "This script requires three, four or five arguments"
fi

BUILD="$1"
if [ "$2" == "snapshot" ]
then
	[ "$#" -ge "3" ] && VERS=$3 || VERS=`date +%Y-%m-%d`
	run ../metro target/build: $BUILD target: snapshot target/version: $VERS || die "snapshot failure"
else
	ARCH="$2"
	SUBARCH="$3"
	extras=""
	if [ "$#" -ge "4" ]
	then
		MODE=$4
		modesp="${4#*+}"
		if [ "$modesp" != "$MODE" ]; then
			extras=$modesp
			MODE="${4%%+*}"
		fi
	else
		MODE=full
	fi
	[ "$#" -ge "5" ] && VERS=$5 || VERS=`date +%Y-%m-%d`
	if [ -n "$extras" ]; then
		extras="multi/extras: $extras"
	fi
	if [ "$MODE" == "test" ]; then
		extras="$extras target: stage3-test"
	else
		extras="$extras multi: yes multi/mode: $MODE"
	fi
	run ../metro -d target/build: $BUILD target/arch_desc: $ARCH target/subarch: $SUBARCH target/version: $VERS $extras || die "build failure"
	exit $?
fi

