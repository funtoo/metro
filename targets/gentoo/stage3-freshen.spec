[collect ./stage/main.spec]
[collect ./stage/capture/tar.spec]
[collect ./stage/stage3-generator.spec]
[collect ./stage/stage3-derivative.spec]

[section target]

type: binary-image

[section steps]

chroot/run: [
#!/bin/bash
$[[steps/setup]]
USE="build" emerge --oneshot --nodeps $eopts portage || exit 1
export USE="$[portage/USE] bindist"
emerge $eopts --deep --newuse -u system || exit 1
if [ "$[emerge/packages/force?]" = "yes" ]
then
	emerge --deep --newuse -u $eopts $[emerge/packages/force:lax] || exit 2
fi
# now, zap the world file....
rm -f /var/lib/portage/world || exit 4
if [ "$[emerge/packages?]" = "yes" ]
then
	emerge --deep --newuse -u $eopts $[emerge/packages:lax] || exit 1
fi
if [ "`emerge --list-sets | grep preserved-rebuild`" = "preserved-rebuild" ]
then
	emerge $eopts @preserved-rebuild || exit 3
fi
# to handle lib upgrades, etc.
]
#make sure the parser detects stray data out here....
[section portage]

ROOT: /


