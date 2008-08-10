#!/bin/bash

. ${clst_sharedir}/targets/support/functions.sh
. ${clst_sharedir}/targets/support/filesystem-functions.sh

case ${1} in
	build_packages)
		echo ">>> Building packages ..."
		shift
		clst_root_path="/" \
		clst_packages="$*" \
		exec_in_chroot \
		${clst_sharedir}/targets/${clst_target}/${clst_target}-pkg.sh
	;;
	pre-kmerge)
		# Sets up the build environment before any kernels are compiled
		if [ -z "${clst_netboot2_busybox_config}" ]; then
			cp ${clst_sharedir}/targets/netboot2/nb-busybox.cf ${clst_chroot_path}/tmp/busy-config
		else
			cp ${clst_netboot2_busybox_config} ${clst_chroot_path}/tmp/busy-config
		fi
		exec_in_chroot ${clst_sharedir}/targets/support/pre-kmerge.sh
	;;
	post-kmerge)
		# Cleans up the build environment after the kernels are compiled
		exec_in_chroot ${clst_sharedir}/targets/support/post-kmerge.sh
	;;
	kernel)
		shift
		export clst_kname="$1"

		# if we have our own linuxrc, copy it in
		if [ -n "${clst_linuxrc}" ]
		then
			cp -pPR ${clst_linuxrc} ${clst_chroot_path}/tmp/linuxrc
		fi
		exec_in_chroot ${clst_sharedir}/targets/support/kmerge.sh
		delete_from_chroot tmp/linuxrc

		extract_modules ${clst_chroot_path} ${clst_kname}
		#16:12 <@solar> kernel_name=foo
		#16:13 <@solar> eval clst_boot_kernel_${kernel_name}_config=bar
		#16:13 <@solar> eval echo \$clst_boot_kernel_${kernel_name}_config
	;;
	image)
		# Creates the base initramfs image for the netboot
		echo -e ">>> Preparing Image ..."
		shift

		# Copy remaining files over to the initramfs target
		clst_files="${@}" \
		exec_in_chroot \
		${clst_sharedir}/targets/${clst_target}/${clst_target}-copyfile.sh
	;;
	final)
		# For each arch, fetch the kernel images and put them in builds/
		echo -e ">>> Copying completed kernels to ${clst_target_path} ..."
		${clst_sharedir}/targets/support/netboot2-final.sh
	;;
	clean)
		exit 0;;
	*)
		exit 1;;
esac

exit $?
