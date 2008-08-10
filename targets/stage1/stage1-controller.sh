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
		ln -s ../usr/portage/profiles/${clst_profile} ${clst_chroot_path}/etc/make.profile

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
