[collect ./stage/main.spec]
[collect ./stage/capture/tar.spec]

[section target]

# change prefix: below to specify the name of your custom stage...

prefix: stage4

[section steps]

chroot/run: [
#!/bin/bash
$[[steps/setup]]
export USE="$[portage/USE] bindist"
emerge $eopts $[emerge/packages] || exit 1
]

[section portage]

ROOT: /
