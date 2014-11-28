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

  Usage: $0 build arch [ full|freshen|quick [date] ]
  Examples:
  	# $0 funtoo-stable generic_64
	# $0 funtoo-current core2_32 freshen
	# $0 gentoo pentium4 full 2009.01.03
EOF
}

if [ $# -lt 2 ] || [ $# -gt 4 ]
then
	do_help
	die "This script requires two, three or four arguments"
fi

BUILD="$1"
if [ "$2" == "snapshot" ]
then
	[ "$#" -ge "3" ] && VERS=$3 || VERS=`date +%Y-%m-%d`
	run ../metro target/build: $BUILD target: snapshot target/version: $VERS || die "snapshot failure"
else
	SUBARCH="$2"
	extras=""
	if [ "$#" -ge "3" ]
	then
		MODE=$3
		modesp="${3##*+}"
		if [ "$modesp" != "$MODE" ]; then
			extras=$modesp
			MODE="${3%%+*}"
		fi
	else
		MODE=full
	fi
	[ "$#" -ge "4" ] && VERS=$4 || VERS=`date +%Y-%m-%d`
	if [ -n "$extras" ]; then
		extras="multi/extras: $extras"
	fi
	run ../metro -d multi: yes target/build: $BUILD target/subarch: $SUBARCH target/version: $VERS multi/mode: $MODE $extras || die "build failure"
	exit $?
fi

