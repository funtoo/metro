
. ${clst_sharedir}/targets/support/functions.sh
. ${clst_sharedir}/targets/support/filesystem-functions.sh

case $1 in
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

	preclean)
		# Move over the motd (if applicable)
		if [ -n "${clst_livecd_motd}" ]
		then
			case ${clst_livecd_type} in
				gentoo-*)
					echo "Using livecd/motd is not supported with livecd/type"
					echo "${clst_livecd_type}. You should switch to using"
					echo "generic-livecd instead."
					cp -pPR ${clst_sharedir}/livecd/files/generic.motd.txt \
						${clst_sharedir}/livecd/files/universal.motd.txt \
						${clst_sharedir}/livecd/files/minimal.motd.txt \
						${clst_sharedir}/livecd/files/livecd.motd.txt \
						${clst_sharedir}/livecd/files/gamecd.motd.txt \
						${clst_chroot_path}/etc
				;;
				*)
					cp -pPR ${clst_livecd_motd} ${clst_chroot_path}/etc/motd
				;;
			esac
		elif [ "${clst_livecd_type}" != "generic-livecd" ]
		then
			cp -pPR ${clst_sharedir}/livecd/files/generic.motd.txt \
				${clst_sharedir}/livecd/files/universal.motd.txt \
				${clst_sharedir}/livecd/files/minimal.motd.txt \
				${clst_sharedir}/livecd/files/livecd.motd.txt \
				${clst_sharedir}/livecd/files/gamecd.motd.txt \
				${clst_chroot_path}/etc
		fi
	
		# move over the environment
		cp -f ${clst_sharedir}/livecd/files/livecd-bashrc \
			${clst_chroot_path}/root/.bashrc
		cp -f ${clst_sharedir}/livecd/files/livecd-bash_profile \
			${clst_chroot_path}/root/.bash_profile
		cp -f ${clst_sharedir}/livecd/files/livecd-local.start \
			${clst_chroot_path}/etc/conf.d/local.start
		
		# execute copy gamecd.conf if we're a gamecd
		if [ "${clst_livecd_type}" = "gentoo-gamecd" ]
		then
			if [ -n "${clst_gamecd_conf}" ]
			then
				cp -f ${clst_gamecd_conf} ${clst_chroot_path}/tmp/gamecd.conf
			else
				echo "gamecd/conf is required for a gamecd!"
				exit 1
			fi
		fi
		;;
	livecd-update)
		# Now, finalize and tweak the livecd fs (inside of the chroot)
		exec_in_chroot ${clst_sharedir}/targets/support/livecdfs-update.sh

		# Move over the xinitrc (if applicable)
		# This is moved here, so we can override any default xinitrc
		if [ -n "${clst_livecd_xinitrc}" ]
		then
			mkdir -p ${clst_chroot_path}/etc/X11/xinit
			cp -f ${clst_livecd_xinitrc} \
				${clst_chroot_path}/etc/X11/xinit/xinitrc
		fi
		;;
	rc-update)
		exec_in_chroot ${clst_sharedir}/targets/support/rc-update.sh
		;;
	fsscript)
		exec_in_chroot ${clst_fsscript}
		;;
	clean)
		find ${clst_chroot_path}/usr/lib -iname "*.pyc" -exec rm -f {} \;
		;;
	bootloader)
		shift
		# Here is where we poke in our identifier
		touch $1/livecd
		
		# Move over the readme (if applicable)
		if [ -n "${clst_livecd_readme}" ]
		then
			cp -f ${clst_livecd_readme} $1/README.txt
		else
			cp -f ${clst_sharedir}/livecd/files/README.txt $1
		fi

		# Move over Getting_Online.txt for minimal/GameCD
		if [ "${clst_livecd_type}" = "gentoo-gamecd" ] \
		|| [ "${clst_livecd_type}" = "gentoo-release-minimal" ] \
		|| [ "${clst_livecd_type}" = "gentoo-release-livecd" ]
		then
			cp -f ${clst_sharedir}/livecd/files/Getting_Online.txt $1
		fi
		
		${clst_sharedir}/targets/support/bootloader-setup.sh $1
		;;
    unmerge)
        shift
        export clst_packages="$*"
        exec_in_chroot ${clst_sharedir}/targets/support/unmerge.sh
    ;;
	target_image_setup)
		shift
		${clst_sharedir}/targets/support/target_image_setup.sh $1
		;;
	iso)
		shift
		${clst_sharedir}/targets/support/create-iso.sh $1
		;;
esac
exit $?
