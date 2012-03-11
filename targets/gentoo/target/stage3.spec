[collect ./stage.spec]
[collect ../steps/symlink.spec]

[section target]

name: stage3-$[:subarch]-$[:build]-$[:version]
name/current: stage3-current

[section trigger]

ok/run: [
#!/bin/bash

install -d $[path/mirror/control]/version || exit 1
echo "$[target/version]" > $[path/mirror/control]/version/stage3 || exit 1

$[[trigger/ok/symlink]]
]
