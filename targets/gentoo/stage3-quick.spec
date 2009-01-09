[collect $[path/metro]/targets/gentoo/stage/main.spec]

[section steps]

chroot/run: [
#!/bin/bash
$[[steps/setup]]
export ROOT=$[portage/ROOT]
USE="build" emerge --oneshot --nodeps portage || exit 1
export USE="$[portage/USE] bindist"
emerge $[emerge/options] system || exit 1
# we are using a non-/ ROOT, so zapping the world file should not be necessary...
if [ "$[emerge/packages?]" = "yes" ]
then
	emerge $[emerge/options] $[emerge/packages:lax] || exit 1
fi
]

[section portage]

ROOT: /tmp/stage3root
