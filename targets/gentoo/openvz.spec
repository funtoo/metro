[collect ./stage/container.spec]

[section target]

name: funtoo-openvz-$[:subarch]-$[:build]-$[:version]
sys: openvz
realname: OpenVZ
url: http://www.openvz.org

[section path/mirror]

target: $[:target/openvz/subpath]/$[target/name].tar.$[target/compression]

[section steps]

chroot/run: [
$[[steps/chroot/run/container/base]]
]


