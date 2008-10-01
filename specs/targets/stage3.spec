metro/class: stage
source: stage2
source/lastdate: << $[version]
source/subarch: << $[subarch]
target: stage3
ROOT: /

chroot/run: [
	>> chroot/setup
	export USE="$[USE] bindist"
	USE="build" emerge --oneshot --nodeps portage || exit 1
	emerge $[emerge/options] -e system || exit 1
	if [ "$[emerge/packages]" != "" ]
	then
		emerge $[emerge/options] $[emerge/packages] || exit 1
	fi
]
