[collect ./files.spec]
[collect ../steps/chroot.spec]
[collect ../steps/setup.spec]
[collect ../steps/unpack.spec]
[collect ../snapshot/global.spec]

[section portage]

ACCEPT_KEYWORDS: $[portage/stable]$[target/arch]

[section metro]

class: stage

[section target]

type: image

[section path]

chroot: $[path/work]
chroot/stage: $[path/work]$[portage/ROOT]

[section steps]

unpack: [
#!/bin/bash
$[[steps/unpack/source]]
$[[steps/unpack/snapshot]]
$[[steps/unpack/env]]
]
