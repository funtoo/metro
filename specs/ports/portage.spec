[section snapshot]

: portage
type: git
path: /root/git/portage
branch: gentoo.org

[section portage]

USE: 
prefix:
ACCEPT_KEYWORDS: $[portage/prefix]$[subarch]
profile: default/linux/$[subarch/arch]/2008.0

[section emerge]

packages: 
