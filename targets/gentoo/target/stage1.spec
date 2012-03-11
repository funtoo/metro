[collect ./stage.spec]

[section target]

name: stage1-$[:subarch]-$[:build]-$[:version]

[section trigger]

ok/run: [
#!/bin/bash

install -d $[path/mirror/control]/version || exit 1
echo "$[target/version]" > $[path/mirror/control]/version/stage1 || exit 1
]
