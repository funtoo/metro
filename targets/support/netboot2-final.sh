#!/bin/bash

. ${clst_sharedir}/targets/support/functions.sh
. ${clst_sharedir}/targets/support/filesystem-functions.sh


extract_kernels ${clst_target_path}boot

# Move kernel binaries to ${clst_target_path}kernels, and
# move everything else to ${clst_target_path}kernels/misc
mkdir ${clst_target_path}kernels
mkdir ${clst_target_path}kernels/misc

for x in ${clst_boot_kernel}; do
	mv ${clst_target_path}boot/${x} ${clst_target_path}kernels
	mv ${clst_target_path}boot/${x}.igz ${clst_target_path}kernels/misc
	mv ${clst_target_path}boot/System.map* ${clst_target_path}kernels/misc/System.map-${x}
done

rmdir ${clst_target_path}boot

# Any post-processing necessary for each architecture can be done here.  This
# may include things like sparc's elftoaout, x86's PXE boot, etc.
case ${clst_hostarch} in
	alpha)
		sleep 0
		;;
	arm)
		sleep 0
		;;
	hppa)
		sleep 0
		;;
	sparc*)
		if [ "${clst_hostarch}" == "sparc" ]; then
			piggyback=piggyback
		else
			piggyback=piggyback64
		fi
		for x in ${clst_boot_kernel}; do
			elftoaout ${clst_target_path}/kernels/${x} -o ${clst_target_path}${x}-a.out
			${piggyback} ${clst_target_path}/${x}-a.out ${clst_target_path}kernels/misc/System.map-${x} ${clst_target_path}kernels/misc/${x}.igz
		done
		;;
	ia64)
		sleep 0
		;;
	x86|amd64)
		sleep 0
		;;
esac
exit $?
