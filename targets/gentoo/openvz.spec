[collect ./source/stage3.spec]
[collect ./target/stage4.spec]
[collect ./steps/container.spec]
[collect ./steps/capture/tar.spec]

[section stage4]

target/name: openvz

[section target]

sys: openvz

[section steps]

chroot/run: [
$[[steps/chroot/run/container/base]]
]
