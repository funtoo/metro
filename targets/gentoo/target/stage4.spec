[collect ./stage.spec]
[collect ../steps/symlink.spec]

[section target]

name: $[stage4/target/name]-$[:subarch]-$[:build]-$[:version]
name/current: $[stage4/target/name]-current

[section trigger]

ok/run: [
#!/bin/bash

install -d $[path/mirror/control]/version/stage4 || exit 1
echo "$[target/version]" > $[path/mirror/control]/version/stage4/$[stage4/target/name] || exit 1

$[[trigger/ok/symlink]]
]

[section portage]

ROOT: /
