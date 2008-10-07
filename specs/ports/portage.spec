[section snapshot]

: portage
type: git
path: /root/git/portage
branch: gentoo.org

[section portage]

USE: 
keyword/prefix:
ACCEPT_KEYWORDS: $[keyword/prefix]$[arch]
profile: default/linux/$[arch]/2008.0

[section emerge]

packages: 
options: 

