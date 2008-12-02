[collect $[path/metro]/targets/gentoo/stage/main.spec]

[section steps]

chroot/run: [
#!/bin/bash
$[[steps/setup]]
export ROOT=$[portage/ROOT]
USE="build" emerge --oneshot --nodeps portage || exit 1
export USE="$[portage/USE] bindist"
emerge $[emerge/options] system || exit 1
if [ "$[emerge/packages]" != "" ]
then
	emerge $[emerge/options] $[emerge/packages] || exit 1
fi
]

[section portage]

ROOT: /tmp/stage3root


