#!/bin/bash

. ${clst_sharedir}/targets/support/functions.sh
. ${clst_sharedir}/targets/support/filesystem-functions.sh

case ${1} in
	enter)
	;;

	build_packages)
		shift
		export clst_packages="$*"
		exec_in_chroot \
			${clst_sharedir}/targets/${clst_target}/${clst_target}-chroot.sh
	;;

	preclean)
	;;

#	package)
#		export root_fs_path="${clst_chroot_path}/tmp/mergeroot"
#		install -d ${clst_image_path}
		
#		${clst_sharedir}/targets/embedded/embedded-fs-runscript.sh \
#			${clst_embedded_fs_type} || exit 1
#		imagesize=`du -sk ${clst_image_path}/root.img | cut -f1`
#		echo "Created ${clst_embedded_fs_type} image at \
#			${clst_image_path}/root.img"
#		echo "Image size: ${imagesize}k"
#	;;

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
		export clst_kname="${1}"
		# if we have our own linuxrc, copy it in
		if [ -n "${clst_linuxrc}" ]
		then
			cp -pPR ${clst_linuxrc} ${clst_chroot_path}/tmp/linuxrc
		fi
		exec_in_chroot ${clst_sharedir}/targets/support/kmerge.sh
		delete_from_chroot tmp/linuxrc
	;;

	target_image_setup)
		shift
		${clst_sharedir}/targets/support/target_image_setup.sh ${1}

	;;
	livecd-update)
		# Now, finalize and tweak the livecd fs (inside of the chroot)
		exec_in_chroot  ${clst_sharedir}/targets/support/livecdfs-update.sh
	;;

	bootloader)
		shift
		# Here is where we poke in our identifier
		touch ${1}/livecd

		${clst_sharedir}/targets/support/bootloader-setup.sh ${1}
	;;
	
	iso)
		shift
		${clst_sharedir}/targets/support/create-iso.sh ${1}
	;;

	clean)
	;;

	*)
	;;

esac
exit $?
