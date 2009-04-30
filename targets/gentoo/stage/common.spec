[collect ./files.spec]
[collect ./steps.spec]
[collect ../snapshot/global.spec]

[section portage]

ACCEPT_KEYWORDS: $[portage/stable]$[target/arch]

[section metro]

class: stage

[section target]

[collect ../../../subarch/$[target/subarch].spec]

[section path]

chroot: $[path/work]
chroot/stage: $[path/work]$[portage/ROOT]
