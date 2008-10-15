[section portage]

name: funtoo-$[target/version]
USE: $[portage/HOSTUSE]
MAKEOPTS: -j2

[section emerge]

options: --jobs=6 --load-average=4
