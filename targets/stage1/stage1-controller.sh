#!/bin/bash

. ${clst_sharedir}/targets/support/functions.sh

case $1 in
	enter)
	;;
	run)
		cp ${clst_sharedir}/targets/stage1/build.py ${clst_chroot_path}/tmp
		
		# Setup "ROOT in chroot" dir
		install -d ${clst_chroot_path}/${clst_root_path}/etc
		
		
		# drobbins fix for building new 2008.0 stages with updated profile link. Let's make
		# sure it's correct and matches what is in the profile.

		rm ${clst_chroot_path}/etc/make.profile
		ln -s /usr/portage/profiles/${clst_profile} ${clst_chroot_path}/etc/make.profile
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
		# Setup make.conf and make.profile link in "ROOT in chroot":
		copy_to_chroot ${clst_chroot_path}/etc/make.conf /${clst_root_path}/etc
		copy_to_chroot ${clst_chroot_path}/etc/make.profile \
			/${clst_root_path}/etc
		# Enter chroot, execute our build script
		exec_in_chroot \
			${clst_sharedir}/targets/${clst_target}/${clst_target}-chroot.sh \
			|| exit 1
	;;
	preclean)
		# Before we enter the chroot, we need to run gcc-config/binutils-config
		if [ -x /usr/bin/gcc-config ] && [ -z "${clst_FETCH}" ]
		then
			mythang=$( cd ${clst_chroot_path}/tmp/stage1root/etc/env.d/gcc; ls ${clst_CHOST}-* | head -n 1 )
			if [ -z "${mythang}" ]
			then
				mythang=1
			fi
			ROOT=${clst_chroot_path}/tmp/stage1root/ \
			CHOST=${clst_CHOST} \
				gcc-config ${mythang}
		fi
		if [ -x /usr/bin/binutils-config ] && [ -z "${clst_FETCH}" ]
		then
			mythang=$( cd ${clst_chroot_path}/tmp/stage1root/etc/env.d/binutils; ls ${clst_CHOST}-* | head -n 1 )
			if [ -z "${mythang}" ]
			then
				mythang=1
			fi
			ROOT=${clst_chroot_path}/tmp/stage1root/ \
			CHOST=${clst_CHOST} \
				binutils-config ${mythang}
		fi
		${clst_CHROOT} ${clst_chroot_path}/tmp/stage1root \
			/usr/sbin/env-update || exit 1

		exec_in_chroot ${clst_sharedir}/targets/${clst_target}/${clst_target}-preclean-chroot.sh /tmp/stage1root || exit 1
	;;
	clean)
		# Clean out man, info and doc files
		rm -rf usr/share/{man,doc,info}/*
		# Zap all .pyc and .pyo files
		find . -iname "*.py[co]" -exec rm -f {} \;
		# Cleanup all .a files except libgcc.a, *_nonshared.a and
		# /usr/lib/portage/bin/*.a
		find . -type f -iname "*.a" | grep -v 'libgcc.a' | grep -v 'nonshared.a' \
			| grep -v '/usr/lib/portage/bin/' | grep -v 'libgcc_eh.a' | xargs \
			rm -f
	;;
	*)
		exit 1
	;;
esac
exit $?
