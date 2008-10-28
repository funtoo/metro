[collect $[path/metro]/specs/arch/$[target/subarch].spec]
[collect $[path/metro]/etc/stage/files.conf]
[collect $[path/metro]/etc/stage/steps.conf]

[section target]

class: stage

[section steps]

chroot/run: [
#!/bin/bash
$[[chroot/setup]]
export USE="$[portage/USE] bindist"
emerge $[emerge/packages] || exit 1
]

[section portage]

ROOT: /
