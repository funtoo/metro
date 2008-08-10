#!/bin/bash

. ${clst_sharedir}/targets/support/functions.sh

case $1 in
	run)
		shift
		exec_in_chroot ${clst_sharedir}/targets/tinderbox/tinderbox-chroot.sh
	;;
	preclean)
		#exec_in_chroot ${clst_sharedir}/targets/tinderbox/tinderbox-preclean-chroot.sh
		delete_from_chroot /tmp/chroot-functions.sh
	;;
	clean)
		exit 0
	;;
	*)
		exit 1
	;;
esac
exit $?
