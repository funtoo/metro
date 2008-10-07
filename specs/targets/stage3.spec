[section target]

: stage3
class: stage
subarch: $[subarch]
version: 2008.10.10

[section source]

: stage2
version: $[target/version]
subarch: $[subarch]

[section chroot]

ROOT: /
run: [
	>> files/setup
	USE="build" emerge --oneshot --nodeps portage || exit 1
	export USE="$[portage/USE] $[subarch/HOSTUSE] bindist"
	emerge $[emerge/options] -e system || exit 1
	if [ "$[emerge/packages]" != "" ]
	then
		emerge $[emerge/options] $[emerge/packages] || exit 1
	fi
]
