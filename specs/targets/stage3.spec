target: stage3

chroot/run: [
	>> chroot/setup
	export USE="$[USE] bindist"
	USE="build" emerge --oneshot --nodeps portage || exit 1
	emerge -e system || exit 1
]
