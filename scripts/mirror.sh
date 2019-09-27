#!/bin/bash
if [ -e ~/.bash_login ]; then
	source ~/.bash_login
fi
mp=$(/root/metro/metro -k path/mirror 2>/dev/null)
/root/metro/scripts/buildrepo clean | tee /tmp/foo.sh
sh /tmp/foo.sh
/root/metro/scripts/buildrepo digestgen
for x in $(/root/metro/scripts/buildrepo fails 2>/dev/null | cut -f8  -d' '); do
		subarch=${x##*/}
		arch=${x%/*}; arch=${arch##*/}
		build=${x%/*}; build=${build%/*}; build=${build##*/}
		echo arch $arch subarch $subarch build $build
		rsync -rltJOve ssh --delete --partial --progress --exclude stage1*.tar* --exclude stage2*.tar* $mp/$build/$arch/$subarch drobbins@upload.funtoo.org:/home/mirror/funtoo/$build/$arch/
		ssh drobbins@upload.funtoo.org sudo /root/metro/scripts/buildrepo index.xml
done
