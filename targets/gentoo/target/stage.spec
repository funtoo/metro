[collect ../steps/unpack.spec]
[collect ../steps/stage.spec]
[collect ./files.spec]

[section target]

class: stage

[section path]

chroot: $[path/work]
chroot/stage: $[path/work]$[portage/ROOT]

[section portage]

ACCEPT_KEYWORDS: $[portage/stable?]$[target/arch:zap]

[section steps]

unpack: [
#!/bin/bash
$[[steps/unpack/source]]
$[[steps/unpack/snapshot]]
$[[steps/unpack/env]]
]
