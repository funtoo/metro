[section portage]

name: funtoo-$[target/version]
USE: $[portage/HOSTUSE]
MAKEOPTS: -j2
ACCEPT_KEYWORDS: ~$[target/arch]

[section emerge]

options: --jobs=6 --load-average=4
packages: net-misc/dhcpcd dev-util/git
