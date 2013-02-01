[collect ./source/stage3.spec]
[collect ./target/stage4-common.spec]
[collect ./steps/container.spec]
[collect ./steps/capture/tar.spec]

[section stage4]

target/name: openvz

[section target]

sys: openvz
name: $[:build]-$[:subarch]-$[stage4/target/name]-$[:version]
name/latest: $[:build]-$[stage4/target/name]-$[path/mirror/link/suffix]
name/full_latest: $[:build]-$[:subarch]-$[stage4/target/name]-$[path/mirror/link/suffix]

[section steps]

chroot/run: [
$[[steps/chroot/run/container/base]]
]
