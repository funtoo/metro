#!/bin/bash

. ${clst_sharedir}/targets/support/functions.sh

# Only put commands in this section that you want every target to execute.
# This is a global default file and will affect every target
case $1 in
	enter)
		${clst_CHROOT} ${clst_chroot_path}
	;;
	pre-kmerge)
		# Sets up the build environment before any kernels are compiled
		exec_in_chroot ${clst_sharedir}/targets/support/pre-kmerge.sh
	;;
	post-kmerge)
		# Cleans up the build environment after the kernels are compiled
		exec_in_chroot ${clst_sharedir}/targets/support/post-kmerge.sh
	;;
	kernel)
		shift
		export clst_kname="$1"
		# If we have our own linuxrc, copy it in
		if [ -n "${clst_linuxrc}" ]
		then
			cp -pPR ${clst_linuxrc} ${clst_chroot_path}/tmp/linuxrc
		fi
		exec_in_chroot ${clst_sharedir}/targets/support/kmerge.sh
		delete_from_chroot tmp/linuxrc
		extract_modules ${clst_chroot_path} ${clst_kname}
		# Do we need this one?
#		extract_kernel ${clst_chroot_path}/boot ${clst_kname}
	;;
	build_packages)
		shift
		export clst_packages="$*"
		exec_in_chroot ${clst_sharedir}/targets/${clst_target}/${clst_target}-chroot.sh
	;;
	preclean)
		exec_in_chroot ${clst_sharedir}/targets/${clst_target}/${clst_target}-preclean-chroot.sh ${clst_root_path}
	;;
	rc-update)
		exec_in_chroot ${clst_sharedir}/targets/support/rc-update.sh
	;;
	fsscript)
		exec_in_chroot ${clst_fsscript}
	;;
	livecd-update)
		# Now, finalize and tweak the livecd fs (inside of the chroot)
		exec_in_chroot ${clst_sharedir}/targets/support/livecdfs-update.sh

		# Move over the xinitrc (if applicable)
		# This is moved here, so we can override any default xinitrc
		if [ -n "${clst_livecd_xinitrc}" ]
		then
			cp -f ${clst_livecd_xinitrc} \
				${clst_chroot_path}/etc/X11/xinit/xinitrc
		fi
	;;
	bootloader)
		exit 0
	;;
	target_image_setup)
		shift
		${clst_sharedir}/targets/support/target_image_setup.sh $1
	;;
	unmerge)
		shift
		export clst_packages="$*"
		exec_in_chroot ${clst_sharedir}/targets/support/unmerge.sh 
	;;
	iso)
		shift
		${clst_sharedir}/targets/support/create-iso.sh $1
	;;
	clean)
		exit 0
	;;
	*)
		exit 1
	;;
esac
exit $?
