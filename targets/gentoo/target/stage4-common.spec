[collect ./stage.spec]
[collect ../steps/symlink.spec]

[section trigger]

ok/run: [
#!/bin/bash

install -d $[path/mirror/target/control]/version/stage4 || exit 1
echo "$[target/version]" > $[path/mirror/target/control]/version/stage4/$[stage4/target/name] || exit 1

$[[trigger/ok/symlink]]
]

[section portage]

ROOT: /
