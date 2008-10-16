[section portage]

name: portage-$[target/version]
USE: $[portage/HOSTUSE]
MAKEOPTS: -j4
ACCEPT_KEYWORDS: $[target/arch]

[section emerge]

options:
packages:
