[section target]

class: stage
# name is used in /etc/metro.conf for pathing constructs :) ! cool
name: $[]-$[target/subarch]-$[target/version]
#require: portage/ROOT target source subarch/arch subarch portage/profile path/mirror/srcstage path/mirror/deststage path/mirror/snapshot subarch/CHOST 
#recommend: path/distfiles portage/USE subarch/CFLAGS portage/MAKEOPTS  

run: 	>> files/setup
	USE="build" emerge --oneshot --nodeps portage || exit 1
	export USE="$[portage/USE] $[subarch/HOSTUSE] bindist"
	emerge $[emerge/options] -e system || exit 1
	if [ "$[emerge/packages]" != "" ]
	then
		emerge $[emerge/options] $[emerge/packages] || exit 1
	fi
]

[section source]

: stage2
version: $[target/version]
subarch: $[target/subarch]

[section portage]

ROOT: /


