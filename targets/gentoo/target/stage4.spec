[collect ./stage.spec]
[collect ../steps/symlink.spec]

[section target]

name: $[stage4/target/name]-$[:subarch]-$[:build]-$[:version]
name/full_latest: $[stage4/target/name]-$[:subarch]-$[:build]-latest
name/latest: $[stage4/target/name]-latest

[section trigger]

ok/run: [
#!/bin/bash

install -d $[path/mirror/target/control]/version/stage4 || exit 1
echo "$[target/version]" > $[path/mirror/target/control]/version/stage4/$[stage4/target/name] || exit 1

$[[trigger/ok/symlink]]
]

[section portage]

ROOT: /
