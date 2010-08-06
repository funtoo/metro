[section path/mirror]

# "current" symlink:
link: $[]/$[target/build]/$[target/subarch]/$[target/name/current].tar.$[target/compression]
link/dest: $[target/build]-$[target/subarch]-$[target/version]/$[target/name].tar.$[target/compression]

[section trigger]

ok/symlink: [
#!/bin/bash
rm -f $[path/mirror/link]
ln -s $[path/mirror/link/dest] $[path/mirror/link] || exit 3
]

