[collect ../generator/livecd.spec]
[collect ./remote.spec]

[section target]

class: virtualbox

[section quickstart]

profile: [
. profiles/virtualbox-single-disk.sh
. profiles/common/vagrant.sh
stage_uri file://$(ls -1 /tmp/$(basename "$[path/mirror/source]"))
tree_type snapshot file://$(ls -1 /tmp/$(basename "$[path/mirror/snapshot]"))
]

[section trigger]

ok/run: [
#!/bin/bash

install -d $[path/mirror/target/control]/version/$[target/class] || exit 1
echo "$[target/version]" > $[path/mirror/target/control]/version/$[target/class]/$[remote/target/name] || exit 1

$[[trigger/ok/symlink]]
]
