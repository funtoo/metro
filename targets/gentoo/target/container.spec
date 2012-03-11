[collect ../steps/unpack.spec]
[collect ../steps/container.spec]

[section target]

class: chroot

[section path]

chroot: $[path/work]

[section steps]

unpack: [
#!/bin/bash
$[[steps/unpack/source]]
]
