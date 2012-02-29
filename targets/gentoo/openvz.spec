[collect ./stage/container.spec]

[section target]

name: $[:build]-$[:subarch]-$[:version]
sys: openvz
realname: OpenVZ
url: http://www.openvz.org

[section steps]

chroot/run: [
$[[steps/chroot/run/container/base]]
]


