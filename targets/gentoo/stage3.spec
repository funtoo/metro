[collect ./stage/common.spec]
[collect ./stage/capture/tar.spec]
[collect ./stage/stage3-generator.spec]

[section path/mirror]

source: $[:source/subpath]/$[source/name].tar.bz2

[section source]

: stage2
name: $[]-$[:subarch]-$[:version]
version: $[target/version]
subarch: $[target/subarch]
build: $[target/build]

[section steps]

chroot/run: [
#!/bin/bash
$[[steps/setup]]

USE="build" emerge --oneshot --nodeps portage || exit 1
export USE="$[portage/USE] bindist"
emerge $eopts -e system || exit 1

# zap the world file and emerge packages
rm -f /var/lib/portage/world || exit 2
if [ "$[emerge/packages?]" = "yes" ]
then
	emerge $eopts $[emerge/packages:lax] || exit 1
fi

# add default runlevel services
if [ "$[baselayout/services?]" = "yes" ]
then
	for service in $[baselayout/services:lax]
	do
		rc-update add $service default
	done
fi

if [ "$[metro/build]" = "funtoo" ] || [ "$[metro/build]" = "~funtoo" ]
then
	eselect vi set busybox
fi
]

[section portage]

ROOT: /
