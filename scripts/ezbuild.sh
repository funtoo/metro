#!/bin/bash

# If we are running from fcron, we'll have a clean environment and thus won't
# have proxy settings. So let's make sure we have a good Gentoo environment...

source /etc/profile

die() {
	echo $*
	exit 1
}

do_help() {
	cat << EOF

  Metro Automation Engine Script
  by Daniel Robbins (drobbins@funtoo.org)

  Usage: $0 arch [ full|freshen|quick [date] ]
  Examples: 
  	# $0 funtoo amd64
	# $0 ~funtoo core2 freshen
	# $0 gentoo pentium4 full 2009.01.03
EOF
}

if [ ! -e /usr/bin/metro ]
then
	die "Metro is required for build.sh to run"
fi

if [ $# -lt 1 ] || [ $# -gt 4 ]
then
	do_help
	die "This script requires two, three or four arguments"
fi

if [ "$#" = "2" ] || [ "$#" = "3" ]
then
	MODE=$2
else
	MODE=full
fi

if [ "$#" = "3" ]
then
	VERS=$3
else
	VERS=`date +%Y.%m.%d`
fi 

BUILD="$1"
SUBARCH="$2"
mycmd="/usr/bin/metro multi: yes metro/build: $BUILD target/subarch: $SUBARCH target/version: $VERS multi/mode: $MODE"
$mycmd
exit $?
