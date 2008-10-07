[section target]

: stage3
class: stage

[section source]

: stage2
version: $[target/version]
subarch: $[target/subarch]

[section chroot]

ROOT: /
run: [
	>> files/setup
	USE="build" emerge --oneshot --nodeps portage || exit 1
	export USE="$[portage/USE] $[arch/HOSTUSE] bindist"
	emerge $[emerge/options] -e system || exit 1
	if [ "$[emerge/packages]" != "" ]
	then
		emerge $[emerge/options] $[emerge/packages] || exit 1
	fi
]
