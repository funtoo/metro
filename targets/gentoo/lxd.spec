[collect ./source/stage3.spec]
[collect ./target/stage4.spec]
[collect ./steps/container-lxd.spec]
[collect ./steps/capture/lxd-tar.spec]

[section stage4]

target/name: lxd

[section target]

sys: lxc

[section path]

lxd: $[path/tmp]/work/lxd

[section steps]

chroot/run: [
$[[steps/chroot/run/container/base]]
sed -i -E -e '/^[*]\s+soft/d' -e '/^[*]\s+hard/d' /etc/security/limits.conf
]
