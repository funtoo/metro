copy_to_chroot(){
	local file_name=$(basename ${1})
	local dest_dir=${clst_chroot_path}${2}
	if [ "${2}" != "" ]
	then
		echo "copying ${file_name} to ${dest_dir}"
		mkdir -p ${dest_dir}
		cp -pPR ${1} ${dest_dir}
		chmod 755 ${dest_dir}/${file_name}
	else
		echo "copying ${file_name} to ${clst_chroot_path}/tmp"
		mkdir -p ${chroot_path}/tmp
		cp -pPR ${1} ${clst_chroot_path}/tmp
		chmod 755 ${clst_chroot_path}/tmp/${file_name}
	fi
}

delete_from_chroot(){
	if [ -e ${clst_chroot_path}${1} ]
	then
		echo "removing ${clst_chroot_path}${1} from the chroot"
		rm -f ${clst_chroot_path}${1}
	fi
}

exec_in_chroot2() {
	local chrootdir = $1
	local script = $2
	install -d $chrootdir/tmp
	cp $script $chrootdir/tmp
	${clst_CHROOT} ${chrootdir} /tmp/`basename $script` || exit 1
}

exec_in_chroot(){
# Takes the full path to the source file as its argument
# copies the file to the /tmp directory of the chroot
# and executes it.
	local file_name=$(basename ${1})
	local subdir=${2#/}

	if [ "${subdir}" != "" ]
	then
		copy_to_chroot ${1} ${subdir}/tmp/
		chroot_path=${clst_chroot_path}${subdir}
		copy_to_chroot ${clst_sharedir}/targets/support/chroot-functions.sh \
			${subdir}/tmp/
		echo "Running ${file_name} in chroot ${chroot_path}" 
		${clst_CHROOT} ${chroot_path} /tmp/${file_name} || exit 1
	else
		copy_to_chroot ${1} tmp/
		chroot_path=${clst_chroot_path}
		copy_to_chroot ${clst_sharedir}/targets/support/chroot-functions.sh \
			tmp/
		echo "Running ${file_name} in chroot ${chroot_path}" 
		${clst_CHROOT} ${chroot_path}/ /tmp/${file_name} || exit 1
	fi

	rm -f ${chroot_path}/tmp/${file_name}
	if [ "${subdir}" != "" ]
	then
		delete_from_chroot ${subdir}/tmp/${file_name}
		delete_from_chroot ${subdir}/tmp/chroot-functions.sh
	else
		delete_from_chroot tmp/chroot-functions.sh
		delete_from_chroot tmp/${file_name}
	fi
}

#return codes
die() {
	echo "$1"
	exit 1
}
