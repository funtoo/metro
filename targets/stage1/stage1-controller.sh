#!/bin/bash

. ${clst_sharedir}/targets/support/functions.sh

case $1 in
	enter)
	;;
	profile)
		rm -f ${clst_chrootdir}/etc/make.profile || exit 1
		ln -s /usr/portage/profiles/${clst_profile} ${clst_chrootdir}/etc/make.profile || exit 1
	;;
	run)
		cp ${clst_sharedir}/targets/stage1/build.py ${clst_chrootdir}/tmp || exit 1
		
		install -d ${clst_rootdir}/etc || exit 1
		
		# Setup make.conf and make.profile link in "ROOT in chroot":
		copy_to_chroot ${clst_chrootdir}/etc/make.conf ${clst_rootdir}/etc
		copy_to_chroot ${clst_chrootdir}/etc/make.profile ${clst_rootdir}/etc

		# Enter chroot, execute our build script
		exec_in_chroot ${clst_sharedir}/targets/${clst_target}/run.sh || exit 1
	;;
	preclean)
		exec_in_chroot ${clst_sharedir}/targets/${clst_target}/preclean.sh || exit 1
	;;
	clean)
		# exec our clean script within our new stage1 itself - ${clst_rootdir} points inside /tmp/stage1root
		exec_in_chroot2 ${clst_rootdir} ${clst_sharedir}/targets/${clst_target}/clean.sh || exit 1
;;
	*)
		exit 1
	;;
esac
exit $?
