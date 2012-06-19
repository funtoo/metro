[section trigger]

ok/symlink: [
#!/bin/bash
ln -sf $[path/mirror/target/link/dest] $[path/mirror/target/link] || exit 3
]
