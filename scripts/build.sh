#!/bin/bash

# If we are running from fcron, we'll have a clean environment and thus won't have proxy settings. So let's make sure we have a good Gentoo environment...
source /etc/profile

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

TMPDIR=/tmp/cat-eng-$$

do_help() {
	cat << EOF

 Catalyst Automation Engine Script
  by Daniel Robbins (drobbins@funtoo.org)

  Usage: $0 arch [version]
  Example: $0 amd64

EOF
}

if [ $# -gt 2 ]
then
	do_help
	die "This script requires one or two arguments"
fi

TEMPLATEDIR=`metro -k specdir`
if [ ! -d $TEMPLATEDIR ]
then
	die "Spec directory $TEMPLATEDIR (from 'metro -k specdir') does not exist."
fi

if [ "${1:0:1}" = "~" ]
then
	#unstable
	PORTSPEC=$TEMPLATEDIR/ports/funtoo.spec
	BASEARCH=${1:1}
else
	PORTSPEC=$TEMPLATEDIR/ports/portage.spec
	BASEARCH=$1
fi

do_metro() {
	install -d $TMPDIR
	MODE=$1
	shift
	echo `date` "metro $MODE start."
	echo `date` "(logging to $TMPDIR/$MODE.log)"
	metro $* > $TMPDIR/$MODE.log 2>&1
	if [ $? -ne 0 ]
	then
		echo `date` "metro error - see $TMPDIR/$MODE.log"
		exit 1
	else
		echo `date` "metro $MODE finish."
	fi
}

do_everything() {
	do_spec
	SPECOUT=$OUTDIR/$SUBARCH/funtoo-$SUBARCH-$CURDATE/meta
	install -d $SPECOUT
	cp -a $TMPDIR/local.spec $PORTSPEC $TEMPLATEDIR/targets/snapshot.spec $TEMPLATEDIR/targets/stage[123].spec $TEMPLATEDIR/arch/$BASEARCH.spec $SPECOUT
	for x in $SPECOUT/*.spec
	do
		mv $x $x.txt
	done
	do_metro snapshot $TMPDIR/local.spec $PORTSPEC $TEMPLATEDIR/targets/snapshot.spec $TEMPLATEDIR/arch/$BASEARCH.spec
	do_metro stage1 $TMPDIR/local.spec $PORTSPEC $TEMPLATEDIR/targets/stage1.spec $TEMPLATEDIR/arch/$BASEARCH.spec
	do_metro stage2 $TMPDIR/local.spec $PORTSPEC $TEMPLATEDIR/targets/stage2.spec $TEMPLATEDIR/arch/$BASEARCH.spec
	do_metro stage3 $TMPDIR/local.spec $PORTSPEC $TEMPLATEDIR/targets/stage3.spec $TEMPLATEDIR/arch/$BASEARCH.spec
	# update what we will build against next time:
	echo $CURDATE > /home/mirror/linux/$SUBARCH/.control/lastdate
	echo $SUBARCH > /home/mirror/linux/$SUBARCH/.control/subarch
}

do_spec() {
	install -d $TMPDIR
	echo "version: $CURDATE" > $TMPDIR/local.spec
	echo "subarch: $SUBARCH" >> $TMPDIR/local.spec
	echo "Set version to $CURDATE."
	echo "Set subarch to $SUBARCH."
}

do_everything
