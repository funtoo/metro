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

  Usage: $0 arch [ full|freshen|quick [date] ]
  Examples: i
  	# $0 amd64
	# $0 ~core2 freshen
	# $0 pentium full 2009.01.03

EOF
}

if [ ! -e /usr/bin/metro ]
then
	die "/usr/bin/metro is required for build.sh to run"
fi

if [ $# -lt 1 ] || [ $# -gt 3 ]
then
	do_help
	die "This script requires one, two or three arguments"
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

SUBARCH="$1"
if [ "${SUBARCH:0:1}" = "~" ]
then
	BUILD="~funtoo"
	# strip ~ from subarch, as Metro doesn't work this way anymore.
	SUBARCH="${SUBARCH:1}"
else
# for stable builds, we create a traditional portage snapshot that is just a tarball of the physical files
	BUILD="gentoo"
fi
mycmd="/usr/bin/metro multi: yes metro/build: $BUILD target/subarch: $SUBARCH target/version: $VERS multi/mode: $MODE"
cat << EOF

  PLEASE NOTE:
  ============

  As of Metro 1.3.0, the metro command itself can perform all the
  functionality of this script.

  You can perform the same actions as the command above by calling
  Metro as follows:

  $mycmd

  The build will continue in 10 seconds...

EOF
sleep 10
$mycmd
exit $?
