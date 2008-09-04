target: stage2

chroot/run: [
	>> chroot/setup
	/usr/portage/scripts/bootstrap.sh -p
	/usr/portage/scripts/bootstrap.sh || exit 1
]
