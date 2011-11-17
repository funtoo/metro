[collect ./stage/container.spec]

[section target]

name: vserver-$[:subarch]-$[:build]-$[:version]
sys: vserver
realname: Linux-VServer
url: http://linux-vserver.org

[section path/mirror]

target: $[:target/vserver/subpath]/$[target/name].tar.$[target/compression]

[section steps]

chroot/run: [
$[[steps/chroot/run/container/base]]
]
