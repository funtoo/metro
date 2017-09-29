[collect ./source/stage3.spec]
[collect ./target/stage4.spec]
[collect ./steps/container.spec]
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
rm /etc/fstab || exit 1
touch /etc/fstab || exit 2
echo "Creating /etc/fstab.lxc (to be used by host...)"
cat > /etc/fstab.lxc << EOF || exit 20
none /lxc/funtoo/dev/pts devpts defaults 0 0
none /lxc/funtoo/proc proc defaults 0 0
none /lxc/funtoo/sys sysfs defaults 0 0
none /lxc/funtoo/dev/shm tmpfs defaults 0 0
none /lxc/funtoo/libexec/rc/init.d tmpfs defaults 0 0
EOF
]
