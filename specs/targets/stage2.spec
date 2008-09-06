target: stage2
sourceversion: $[version]

chroot/run: [
	>> chroot/setup
	/usr/portage/scripts/bootstrap.sh -p
	/usr/portage/scripts/bootstrap.sh || exit 1
]
