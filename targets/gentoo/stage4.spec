[collect ./stage/common.spec]
[collect ./stage/capture/tar.spec]
[collect ./stage/stage3-derivative.spec]

[section path/mirror]

target: $[:source/subpath]/$[target/name].tar.bz2

[section target]

name: stage4-$[target/subarch]-$[target/version]
type: binary-image

[section steps]

chroot/run: [
#!/bin/bash
$[[steps/setup]]
export USE="$[portage/USE] bindist"
emerge $eopts $[emerge/packages] || exit 1
]

[section portage]

ROOT: /
