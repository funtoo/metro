[section trigger]

ok/symlink: [
#!/bin/bash
rm -f $[path/mirror/stage/link]
ln -s $[path/mirror/stage/link/dest] $[path/mirror/stage/link]
]
