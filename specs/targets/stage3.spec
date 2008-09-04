target: stage3

chroot/run: [
	>> chroot/setup
	export USE="$[USE] bindist"
	USE="build" emerge --oneshot --nodeps portage
	emerge -e system
]
