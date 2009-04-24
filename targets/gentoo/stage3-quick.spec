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
emerge -u portage || exit 1
export ROOT=$[portage/ROOT]
export USE="$[portage/USE] bindist"
emerge $eopts --nodeps sys-apps/baselayout || exit 1
emerge $eopts system || exit 1
# we are using a non-/ ROOT, so zapping the world file should not be necessary...
if [ "$[emerge/packages?]" = "yes" ]
then
	emerge $eopts $[emerge/packages:lax] || exit 1
fi
]

[section portage]

ROOT: /tmp/stage3root
