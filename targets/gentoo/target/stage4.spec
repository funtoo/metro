# This file defines common settings for all stage4 generators. Stage4
# generators are targets that build on top of a stage3 to produce various
# specialized images such as a webserver, database or container images.

[collect ./stage.spec]
[collect ../steps/symlink.spec]

[section target]

name: $[stage4/target/name]-$[:subarch]-$[:build]-$[:version]
name/current: $[stage4/target/name]-current

[section trigger]

ok/run: [
#!/bin/bash

# Since we've completed a successful stage4 build, we will update our
# .control/version/stage4 directory. This file records the version of the last
# successful stage4 build.

install -d $[path/mirror/control]/version/stage4 || exit 1
echo "$[target/version]" > $[path/mirror/control]/version/stage4/$[stage4/target/name] || exit 1

$[[trigger/ok/symlink]]
]

[section portage]

ROOT: /
