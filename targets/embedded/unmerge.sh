
${clst_CHROOT} ${clst_chroot_path} /bin/bash << EOF
	ROOT=/tmp/mergeroot emerge -C $* || exit 1
EOF
