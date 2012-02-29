[collect ./stage/container.spec]

[section target]

name: vserver-$[:subarch]-$[:build]-$[:version]
sys: vserver
realname: Linux-VServer
url: http://linux-vserver.org

[section steps]

chroot/run: [
$[[steps/chroot/run/container/base]]
]
