#
#	This is a useful piece of code to debug various build issues. May add it as a "probes" feature
#	in the future. I used it to find that baselayout-2.0.0 was totally frying /usr/lib/gcc if it
#	was merged after gcc. Now fixed temporarily by forcing baselayout to merge first- zmedico is
#	working on a correct fix.
#
#		# debug GCC issue
#		outfile=/tmp/stage1root/usr/bin/debug.log
#		cat << EOF > ${clst_chroot_path}/etc/portage/bashrc
##!/bin/bash
#SANDBOX_ON=0
#echo \$P \$EBUILD_PHASE >> $outfile
#if [ "\$EBUILD_PHASE" != "depend" ]
#then 
#if [ -d /tmp/stage1root/usr/lib/gcc ]
#then
#	install -d /tmp/stage1root/usr/bin/debug
#	echo "/tmp/stage1root/usr/bin/debug/\$P.\$EBUILD_PHASE.log"  >> $outfile
#	{ cd /tmp/stage1root/usr/lib/gcc; find > /tmp/stage1root/usr/bin/debug/\$P.\$EBUILD_PHASE.log; }
#	echo >> $outfile
#fi
#fi
#SANDBOX_ON=1
#EOF

