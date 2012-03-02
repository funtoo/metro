[collect ./source/stage3.spec]
[collect ./target/stage3.spec]
[collect ./steps/capture/tar.spec]

[section steps]

chroot/run: [
#!/bin/bash
$[[steps/setup]]
USE="build" emerge --oneshot --nodeps $eopts portage || exit 1
export USE="$[portage/USE] bindist"
emerge $eopts --deep --newuse -u @world || exit 1
emerge --deep --newuse -u $eopts $[emerge/packages/force:zap] || exit 2
emerge --deep --newuse -u $eopts $[emerge/packages:zap] || exit 1
if [ "`emerge --list-sets | grep preserved-rebuild`" = "preserved-rebuild" ]
then
	emerge $eopts @preserved-rebuild || exit 3
fi
]

[section portage]

ROOT: /
