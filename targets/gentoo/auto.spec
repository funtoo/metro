[section metro]

class: target

[section target]

type: script

[section steps]

run: [
#!/bin/bash
source /etc/profile

die() {
	echo $*
	exit 1
}


if [ "$[target/version?]" = "yes" ]
then
	CURDATE="$[target/version:lax]"
else
	CURDATE=`date +%Y.%m.%d`
fi

if [ "$[build/mode?]" = "yes" ]
then
	BUILDMODE="$[build/mode:lax]"
else
	BUILDMODE="full"
fi

if [ "$BUILDMODE" = "full" ]
then
	builds="stage1 stage2 stage3"
elif [ "$BUILDMODE" = "quick" ]
then
	builds="stage3-quick"
elif [ "$BUILDMODE" = "freshen" ]
then
	builds="stage3-freshen"
else
	die "Build type \"$BUILDMODE\" not recognized."
fi
SUBARCH="$[target/subarch]"
if [ "${SUBARCH:0:1}" = "~" ]
then
	builds="git-snapshot $builds openvz"
	mb="funtoo"
else
	builds="snapshot $builds"
	mb="gentoo"
fi

MAINARGS="metro/build: $mb target/subarch: $SUBARCH target/version: $CURDATE"
CONTROL=`metro -k path/mirror/control $MAINARGS`
if [ ! -d "$CONTROL" ]
then
	die "Control directory $CONTROL (from 'metro -k path/mirror/control $MAINARGS') does not exist."
fi


for x in $builds
do
	metro $MAINARGS target: $x || die "$x fail: metro failure"
	if [ "${x:0:6}" = "stage3" ]
	then
		echo $CURDATE > ${CONTROL}/lastdate
		echo $SUBARCH > ${CONTROL}/subarch
		CURRENT=`metro -k path/mirror/stage3/current $MAINARGS target: $x`
		TARGET=`metro -k path/mirror/stage3/current/dest $MAINARGS target: $x`
		# update current symlink
		rm -f "$CURRENT"
		ln -s "$TARGET" "$CURRENT"
	fi
done
]
