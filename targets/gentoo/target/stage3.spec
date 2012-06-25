[collect ./stage.spec]
[collect ../steps/symlink.spec]

[section target]

name: stage3-$[:subarch]-$[:build]-$[:version]
name/latest: stage3-latest
name/full_latest: stage3-$[:subarch]-$[:build]-latest

[section trigger]

ok/run: [
#!/bin/bash

install -d $[path/mirror/target/control]/version || exit 1
echo "$[target/version]" > $[path/mirror/target/control]/version/stage3 || exit 1

$[[trigger/ok/symlink]]
]
