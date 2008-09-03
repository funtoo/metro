target: stage2

USE: $[HOSTUSE]

# do the stuff here that you need to do, with bind mounts unmounted (for safety:)
chroot/run: [
	$[chroot/setup]
	/usr/portage/scripts/bootstrap.sh -p
	/usr/portage/scripts/bootstrap.sh || exit 1
]
