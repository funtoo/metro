[collect ./stage/container.spec]

[section target]

name: $[:build]-$[:subarch]-$[:version]
sys: openvz
realname: OpenVZ
url: http://www.openvz.org

[section path/mirror]

target: $[:target/openvz/subpath]/$[target/name].tar.$[target/compression]

[section steps]

chroot/run: [
$[[steps/chroot/run/container/base]]
]


