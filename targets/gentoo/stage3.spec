[collect $[path/metro]/targets/gentoo/stage/main.spec]

[section steps]

chroot/run: [
#!/bin/bash
$[[steps/setup]]
USE="build" emerge --oneshot --nodeps portage || exit 1
export USE="$[portage/USE] bindist"
emerge $[emerge/options] -e system || exit 1
# zap the world file...
rm -f /var/lib/portage/world || exit 2
if [ "$[emerge/packages?]" = "yes" ]
then
	emerge $[emerge/options] $[emerge/packages:lax] || exit 1
fi
]

[section portage]

ROOT: /


