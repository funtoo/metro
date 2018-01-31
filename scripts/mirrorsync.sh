#!/bin/bash
pidfile=/var/tmp/mirrorsync.pid
[ -e "$pidfile" ] && [ -d "/proc/$(cat $pidfile)" ] && echo "mirror operation still running, skipping..." && exit 1
echo $$ > $pidfile
cd /var/tmp || exit 1
ran_clean="no"
try_cleaning() {
	if [ ! -n "$(ls /home/drobbins/.sync-* 2>/dev/null)" ] && [ "$ran_clean" == "no" ]; then
		echo "Cleaning local stage repository..."
		# don't clean while other sync jobs are running.
		/root/metro/scripts/buildrepo clean > clean.sh || exit 1
		sh clean.sh || exit 1
		ran_clean="yes"
	else
		echo "Temporarily skipping clean due to incoming stages (or already cleaned)..."
	fi
}
try_cleaning
opts="--delete --delete-excluded"
rsync --bwlimit=30m --exclude=stage2* --exclude=funtoo-*-next --exclude=stage1* $opts -rtlve ssh /home/mirror/funtoo/ funtoo@ftp-osl.osuosl.org:/data/ftp/pub/funtoo/
ssh funtoo@ftp-osl.osuosl.org chmod -R go+r /data/ftp/pub/funtoo/*
ssh funtoo@ftp-osl.osuosl.org ./trigger-funtoo
rm -f $pidfile
try_cleaning
