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
		exec_in_chroot \
			${clst_sharedir}/targets/${clst_target}/${clst_target}-chroot.sh
	;;
	preclean)
		exec_in_chroot ${clst_sharedir}/targets/${clst_target}/${clst_target}-preclean-chroot.sh ${clst_root_path}
	;;
	clean)
		exit 0
	;;
	*)
		exit 1
	;;
esac
exit $?
