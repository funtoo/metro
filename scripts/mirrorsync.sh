#!/bin/bash
pidfile=/var/tmp/mirrorsync.pid
[ -e "$pidfile" ] && [ -d "/proc/$(cat $pidfile)" ] && echo "mirror operation still running, skipping..." && exit 1
echo $$ > $pidfile
cd /var/tmp || exit 1
/root/git/metro/scripts/buildrepo clean > clean.sh || exit 1
sh clean.sh || exit 1
/root/git/metro/scripts/digestgen || exit 1
remotedir=$(ssh funtoo@ftp-osl.osuosl.org 'ls -d /data/ftp/.[12]/funtoo')
rsync --delete --exclude=stage2*.tar.xz --delete-excluded -rlve ssh /home/mirror/funtoo/ funtoo@ftp-osl.osuosl.org:$remotedir/
ssh funtoo@ftp-osl.osuosl.org chmod -R go+r $remotedir/*
ssh funtoo@ftp-osl.osuosl.org ./trigger-funtoo
rm -f $pidfile

