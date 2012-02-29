[collect ./stage/common.spec]
[collect ./stage/stage3-derivative.spec]
[collect ./steps/capture/tar.spec]
[collect ./steps/symlink.spec]

[section target]

name: $[stage4/name]-$[:subarch]-$[:version]
name/current: $[stage4/name]-$[:subarch]-current

[section steps]

chroot/run: [
#!/bin/bash
$[[steps/setup]]
$[[steps/stage4/run]]
]

[section trigger]

ok/run: [
$[[trigger/ok/symlink]]
]

[section portage]

ROOT: /
