
. ${clst_sharedir}/targets/support/functions.sh

## START RUNSCRIPT

case $1 in
	build_packages)
		shift
		export clst_packages="$*"
		mkdir -p ${clst_chroot_path}/usr/livecd
		exec_in_chroot \
			${clst_sharedir}/targets/${clst_target}/${clst_target}-chroot.sh
		;;
	clean)
		find ${clst_chroot_path}/usr/lib -iname "*.pyc" -exec rm -f {} \;
		;;
esac
exit $?
