# This file defines common settings for all stage3 generators. Stage3
# generators are targets that produce a literal stage3 -- currently these
# targets are stage3, stage3-quick, and stage3-freshen.

[section path/mirror]

target: $[:target/subpath]/stage3-$[target/version].tar.bz2

# "current" symlink:
link: $[]/$[target/build]/$[target/subarch]/$[target/name/current].tar.bz2
link/dest: $[target/build]-$[target/subarch]-$[target/version]/$[target/name].tar.bz2

[section target]

name: stage3-$[target/subarch]-$[target/version]
name/current: stage3-$[target/subarch]-current

[section trigger]

ok/run: [
#!/bin/bash

# UPDATE lastdate and subarch for our next build:
echo "$[target/version]" > $[path/mirror/control]/lastdate || exit 1
echo "$[target/subarch]" > $[path/mirror/control]/subarch || exit 2
echo "$[target/build]" > $[path/mirror/control]/build || exit 2
# CREATE current symlink for the stage3
rm -f $[path/mirror/link]
ln -s $[path/mirror/link/dest] $[path/mirror/link] || exit 3
]

