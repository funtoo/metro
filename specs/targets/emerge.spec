metro/class: stage
source: stage3
target: mystuff
ROOT: /
rootdir: $[workdir]
sourceversion: $[version]

chroot/run: [
	>> chroot/setup
	export USE="$[USE] bindist"
	emerge dhcpcd dev-util/git || exit 1
]

