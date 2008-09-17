target: stage2
sourceversion: $[version]

chroot/run: [
	>> chroot/setup
	export EMERGE_DEFAULT_OPTS=$[emerge/options]
	/usr/portage/scripts/bootstrap.sh -p
	/usr/portage/scripts/bootstrap.sh || exit 1
]
