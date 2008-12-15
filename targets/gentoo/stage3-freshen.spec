[collect $[path/metro]/targets/gentoo/stage/main.spec]

[section steps]

chroot/run: [
#!/bin/bash
$[[steps/setup]]
USE="build" emerge --oneshot --nodeps portage || exit 1
export USE="$[portage/USE] bindist"
emerge $[emerge/options] --deep -u system || exit 1
if [ "$[emerge/packages?]" = "yes" ]
then
	emerge --deep -u $[emerge/options] $[emerge/packages:lax] || exit 1
fi
if [ "$[emerge/packages/force?]" = "yes" ]
then
	emerge -f $[emerge/options] $[emerge/packages/force:lax] || exit 2
fi
]

[section portage]

ROOT: /


