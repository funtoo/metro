[section portage]

name: portage-$[target/version]
USE: $[portage/HOSTUSE]
MAKEOPTS: -j4

[section emerge]

options:
