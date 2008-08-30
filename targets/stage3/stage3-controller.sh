#!/bin/bash

. ${clst_sharedir}/targets/support/functions.sh

# Only put commands in this section that you want every target to execute.
# This is a global default file and will affect every target
case $1 in
	enter)
		${clst_CHROOT} ${clst_chroot_path}
	;;
	run)
		shift
		export clst_packages="$*"
		exec_in_chroot ${clst_sharedir}/targets/${clst_target}/run.sh
	;;
	preclean)
		exec_in_chroot ${clst_sharedir}/targets/${clst_target}/preclean.sh 
	;;
	clean)
		exec_in_chroot2 ${clst_chrootdir} ${clst_sharedir}/targets/${clst_target}/clean.sh 
	;;
	*)
		exit 1
	;;
esac
exit $?
