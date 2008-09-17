target: stage3
sourceversion: $[version]

chroot/run: [
	>> chroot/setup
	export USE="$[USE] bindist"
	USE="build" emerge --oneshot --nodeps portage || exit 1
	emerge $[emerge/options] -e system || exit 1
]
