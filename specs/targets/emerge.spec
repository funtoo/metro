[collect $[path/metro]/specs/arch/$[target/subarch].spec]
[collect $[path/metro]/specs/targets/stage/files.conf]
[collect $[path/metro]/specs/targets/stage/steps.conf]

[section target]

class: stage

[section steps]

chroot/run: [
#!/bin/bash
$[[steps/setup]]
export USE="$[portage/USE] bindist"
emerge $[emerge/packages] || exit 1
]

[section portage]

ROOT: /
