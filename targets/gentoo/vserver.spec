[collect ./source/stage3.spec]
[collect ./target/stage4.spec]
[collect ./steps/container.spec]
[collect ./steps/capture/tar.spec]

[section stage4]

target/name: vserver

[section target]

sys: vserver

[section steps]

chroot/run: [
$[[steps/chroot/run/container/base]]
]
