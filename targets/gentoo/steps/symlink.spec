[section trigger]

ok/symlink: [
#!/bin/bash
rm -f $[path/mirror/target/link]
ln -s $[path/mirror/target/link/dest] $[path/mirror/target/link]
]
