[collect ./source/stage3.spec]
[collect ./target/container.spec]
[collect ./steps/capture/tar.spec]

[section target]

name: openvz-$[:build]-$[:subarch]-$[:version]
sys: openvz
realname: OpenVZ
url: http://www.openvz.org

[section steps]

chroot/run: [
$[[steps/chroot/run/container/base]]
]
