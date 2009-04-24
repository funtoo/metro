[collect ./stage/main.spec]
[collect ./stage/capture/tar.spec]
[collect ./stage/stage3-generator.spec]

[section source]

: stage2
version: $[target/version]
subarch: $[target/subarch]
build: $[target/build]

[section target]

type: binary-image

[section steps]

chroot/run: [
#!/bin/bash
$[[steps/setup]]
USE="build" emerge --oneshot --nodeps portage || exit 1
export USE="$[portage/USE] bindist"
emerge $eopts -e system || exit 1
# zap the world file...
rm -f /var/lib/portage/world || exit 2
if [ "$[emerge/packages?]" = "yes" ]
then
	emerge $eopts $[emerge/packages:lax] || exit 1
fi
if [ "$[metro/build]" = "funtoo" ]
then
	eselect vi set busybox
fi
]

[section portage]

ROOT: /


