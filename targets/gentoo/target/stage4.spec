[collect ./stage.spec]
[collect ../steps/symlink.spec]

[section target]

name: $[:build]-$[:subarch]-$[stage4/target/name]-$[:version]
name/full_latest: $[:build]-$[:subarch]-$[stage4/target/name]-latest
name/latest: $[:build]-$[stage4/target/name]-latest

[section trigger]

ok/run: [
#!/bin/bash

install -d $[path/mirror/target/control]/version/stage4 || exit 1
echo "$[target/version]" > $[path/mirror/target/control]/version/stage4/$[stage4/target/name] || exit 1

$[[trigger/ok/symlink]]
]

[section portage]

ROOT: /
