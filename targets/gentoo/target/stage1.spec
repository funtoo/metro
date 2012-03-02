[collect ./stage.spec]

[section target]

name: $[]-$[:subarch]-$[:build]-$[:version]

[section trigger]

ok/run: [
#!/bin/bash

# Since we've completed a successful stage1 build, we will update our
# .control/version/stage1 file. This file records the version of the last
# successful stage1 build.

install -d $[path/mirror/control]/version || exit 1
echo "$[target/version]" > $[path/mirror/control]/version/stage1 || exit 1
]
