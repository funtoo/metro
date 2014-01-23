[collect ./stage.spec]
[collect ../steps/symlink.spec]

[section target]

base: stage4-$[:subarch]-$[:build]-$[:version]
name: stage4-$[:subarch]-$[:build]-$[:version]-$[:count]
name/latest: stage4-$[path/mirror/link/suffix]
name/full_latest: stage4-$[:subarch]-$[:build]-$[path/mirror/link/suffix]

[section trigger]

ok/run: [
#!/bin/bash

install -d $[path/mirror/target/control]/version || exit 1
echo "$[target/version]" > $[path/mirror/target/control]/version/stage4 || exit 1
echo "$[target/count]" > $[path/mirror/target/control]/version/count || exit 1

$[[trigger/ok/symlink]]
]
