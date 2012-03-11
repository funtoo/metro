[section steps]

chroot/run/container/base: [
#!/bin/bash

if [ -e $TMPDIR/etc/conf.d/rc ]
then
	echo "You appear to be using a Gentoo (non-OpenRC) stage. This target only supports"
	echo "OpenRC-based stages, such as the Funtoo stages. Aborting."
	exit 1
fi

# mounts
echo "Updating mtab and fstab..."
rm -f /etc/mtab
ln -s /proc/mounts /etc/mtab || exit 1
echo "proc /proc proc defaults 0 0" > /etc/fstab

# turn off gettys
echo "Updating inittab..."
sed -i -e '/getty/s/^/#/' /etc/inittab

# reset root password
echo "Updating root password..."
sed -i -e 's/^root:[^:]*:/root:!:/' /etc/shadow

# set proper permissions on /etc/shadow!
chmod 0640 /etc/shadow || exit 2

# device nodes
echo "Creating device nodes..."
[ -e /lib/udev/devices/ttyp0 ] || mknod /lib/udev/devices/ttyp0 c 3 0 || exit 3
[ -e /lib/udev/devices/ptyp0 ] || mknod /lib/udev/devices/ptyp0 c 2 0 || exit 3
[ -e /lib/udev/devices/ptmx ] || mknod /lib/udev/devices/ptmx c 5 2 || exit 3
[ -e /lib/udev/devices/urandom ] || mknod /lib/udev/devices/urandom c 1 9 || exit 3
[ -e /lib/udev/devices/random ] || mknod /lib/udev/devices/random c 1 8 || exit 3
[ -e /lib/udev/devices/zero ] || mknod /lib/udev/devices/zero c 1 5 || exit 3

# timezone
echo "Setting time zone..."
rm -f /etc/localtime
ln -s /usr/share/zoneinfo/UTC /etc/localtime || exit 4

# sshd
echo "Adding sshd to default runlevel..."
rc-update add sshd default

echo "Removing unnecessary udev stuff from default runlevel..."
rc-update del udev-mount sysinit
rc-update del udevd sysinit

# hostname - change periods from target/name into dashes
echo "Setting hostname..."
myhost=$(echo $[target/name] | tr . -)
cat > /etc/conf.d/hostname << EOF || exit 5
# /etc/conf.d/hostname

# Set to the hostname of this machine
hostname=${myhost}
EOF

# cleanup
rm -rf /etc/ssh/ssh_host* /var/tmp/* /var/log/* /tmp/* /root/.bash_history /etc/resolv.conf

# openrc system id
echo "Setting system type to $[target/sys]..."
echo 'rc_sys="$[target/sys]"' >> /etc/rc.conf

# TESTS
echo "Performing QA checks..."
# root password blank
[ "`cat /etc/shadow | grep ^root | cut -b1-7`" != 'root:!:' ] && exit 15
echo "Root password check: PASSED"
# tty must exist
[ ! -e /dev/tty ] && exit 16
echo "/dev/tty check: PASSED"
]
