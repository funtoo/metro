[collect ./source/stage3.spec]
[collect ./target/stage4.spec]
[collect ./steps/capture/tar.spec]

[section portage]

ROOT: /

[section steps]

chroot/run: [
#!/bin/bash
$[[steps/setup]]

export USE="$[portage/USE] bindist"

# Emerges packages related to the kernel (maybe builds modules)
# without using binary packages.
emerge ${eopts} --usepkg=n $[emerge/rpackages:zap] || exit 1

# Emerge the rest of the packages we want to add to the stage4
emerge ${eopts} $[emerge/packages/first:zap] || exit 2
emerge ${eopts} $[emerge/packages:zap] || exit 2
]
