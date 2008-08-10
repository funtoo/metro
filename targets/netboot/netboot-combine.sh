#!/bin/bash

. ${clst_sharedir}/targets/support/chroot-functions.sh
. ${clst_sharedir}/targets/support/functions.sh
. ${clst_sharedir}/targets/support/filesystem-functions.sh

update_env_settings

setup_myfeatures

# Ssetup our environment
export FEATURES="${clst_myfeatures}"

# First install the boot package that we need
booter=""
case ${clst_hostarch} in
	alpha)
		booter=""
	;;
	arm)
		booter=""
	;;
	hppa)
		booter=palo
	;;
	sparc*)
		booter=sparc-utils
	;;
	x86|amd64)
		booter=netboot
	;;
	*)
		exit 1
	;;
esac

#if [ ! -z "${booter}" ] ; then
#	run_emerge ${booter} || exit 1
#fi

extract_kernels ${clst_chroot_path}/tmp

# Then generate the netboot image ! :D
for kname in ${clst_boot_kernel}
do
	mkdir -p ${clst_chroot_path}/tmp/staging/initrd-${kname}
	cp -r ${clst_chroot_path}/tmp/image ${clst_chroot_path}/tmp/staging/initrd-${kname}
	extract_modules ${clst_chroot_path}/tmp/staging/initrd-${kname} ${kname}
	create_normal_loop ${clst_chroot_path}/tmp/staging/initrd-${kname} ${clst_target_path} initrd-${kname}.igz
	rm -r ${clst_chroot_path}/tmp/staging/initrd-${kname}

	case ${clst_hostarch} in
		alpha)
			# Until aboot is patched this is broken currently.
			# please use catalyst 1.1.5 or older
		
			#TEST TEST TEST TEST
			#http://lists.debian.org/debian-alpha/2004/07/msg00094.html
			#make \
			#		-C /usr/src/linux \
			#		INITRD=/initrd.gz \
			#		HPATH="/usr/src/linux/include" \
			#		vmlinux bootpfile \
			#		|| exit 1
			#cp /usr/src/linux/arch/alpha/boot/bootpfile /netboot.alpha || exit 1
			;;
		arm)
			#TEST TEST TEST TEST
			cp /${clst_chroot_path}/tmp/${kname} /netboot-${kname}.arm || exit 1
			cat /${clst_target_path}/initrd-${kname}.igz >> /${clst_target_path}/netboot-${kname}.arm || exit 1
			#make \
			#	-C /usr/src/linux \
			#	INITRD=/initrd.gz \
			#	bootpImage \
			#	|| exit 1
			;;
		hppa)
			# We have to remove the previous image because the file is
			# considered as a tape by palo and then not truncated but rewritten.
			#TEST TEST TEST TEST
			rm -f /netboot-${kname}.hppa

			palo \
				-k /${clst_chroot_path}/tmp/${kname} \
				-r /${clst_target_path}/initrd-${kname}.igz \
				-s /${clst_target_path}/netboot-${kname}.hppa \
				-f foo \
				-b /usr/share/palo/iplboot \
				-c "0/vmlinux root=/dev/ram0 ${cmdline_opts}" \
				|| exit 1
			;;
		sparc*)
			#TEST TEST TEST TEST
			#elftoaout -o /netboot-${kname}.${clst_hostarch} /usr/src/linux/vmlinux
			#elftoaout -o /netboot-${kname}.${clst_hostarch} /${kname}
			#piggy=${clst_hostarch/sparc/piggyback}
			#${piggy} /netboot-${kname}.${clst_hostarch} /usr/src/linux/System.map /initrd-${kname}.igz
			;;
		x86)
			mknbi-linux \
				-k /${clst_chroot_path}/tmp/${kname} \
				-r /${clst_target_path}/initrd-${kname}.igz \
				-o /${clst_target_path}/netboot-${kname}.x86 \
				-x \
				-a "root=/dev/ram0 ${cmdline_opts}" \
				|| exit 1
			;;
		*)
			exit 1
			;;
	esac
done
