[collect $[path/metro]/targets/gentoo/stage/main.spec]

[section steps]

chroot/run: [
#!/bin/bash
$[[steps/setup]]
export USE="$[portage/USE] bindist"
emerge $[emerge/packages] || exit 1
]

[section portage]

ROOT: /
