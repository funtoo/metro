[collect ./stage/main.spec]
[collect ./stage/capture/tar.spec]

[section steps]

chroot/run: [
#!/bin/bash
$[[steps/setup]]
export USE="$[portage/USE] bindist"
emerge $[emerge/packages] || exit 1
]

[section portage]

ROOT: /
