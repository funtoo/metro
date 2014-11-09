[collect ./stage.spec]

[section target]

name: stage1-$[:subarch]-$[:build]-$[:version]
pkgcache: stage1

[section trigger]

ok/run: [
#!/bin/bash

install -d $[path/mirror/target/control]/version || exit 1
echo "$[target/version]" > $[path/mirror/target/control]/version/stage1 || exit 1
]
