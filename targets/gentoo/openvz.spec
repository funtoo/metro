[collect ./stage/stage3-derivative.spec]

[section metro]

class: chroot

[section target]

type: image
name: funtoo-openvz-$[:subarch]-$[:build]-$[:version]

[section path/mirror]

target: $[:target/subpath]/openvz/$[target/name].tar.$[target/compression]

[section path]

chroot: $[path/work]

[section steps]

unpack: [
#!/bin/bash
[ ! -d $[path/chroot] ] && install -d $[path/chroot]
[ ! -d $[path/chroot]/tmp ] && install -d $[path/chroot]/tmp --mode=1777 || exit 2
src="$(ls $[path/mirror/source])"
comp="${src##*.}"

[ ! -e "$src" ] && echo "Source file $src not found, exiting." && exit 1
echo "Extracting source stage $src..."

case "$comp" in
	bz2)
		if [ -e /usr/bin/pbzip2 ]
		then
			# Use pbzip2 for multi-core acceleration
   			echo "using pbzip2"
			pbzip2 -dc "$src" | tar xpf - -C $[path/chroot] || exit 3
		else
			tar xjpf "$src" -C $[path/chroot] || exit 3
		fi
		;;
	gz|xz)
		tar xpf "$src" -C $[path/chroot] || exit 3
		;;		
	*)
		echo "Unrecognized source compression for $src"
		exit 1
		;;
esac
]

capture: [
#!/bin/bash

die() {
	echo $*
	rm -f $[path/mirror/target]
	exit 1
}

trap "die user interrupt - Removing incomplete template..." INT

rm -rf /tmp/steps || die "Steps cleanup fail"
outdir=`dirname $[path/mirror/target]`
if [ ! -d $outdir ]
then
	install -d $outdir || "Output path $outdir does not exist"
fi
echo "Creating $[path/mirror/target]..."
case "$[target/compression]" in
	bz2)
		comp=j
		;;
	gz)
		comp=z
		;;
	xz)
		comp=J
		;;
	*)
		echo "Unrecognized compression $[target/compression]"
		exit 1
esac


tar c${comp}pf $[path/mirror/target] -C $[path/chroot] .
if [ $? -ge 2 ]
then
	die "Error creating tarball"
fi
]

chroot/run: [
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
	mv /etc/inittab /etc/inittab.orig || exit 2
	cat /etc/inittab.orig | sed -e '/getty/s/^/#/' > /etc/inittab || exit 3
	rm -f /etc/inittab.orig || exit 4

	# reset root password
	echo "Updating root password..."
	cat /etc/shadow | sed -e 's/^root:[^:]*:/root:!:/' > /etc/shadow.new || exit 5
	cat /etc/shadow.new > /etc/shadow || exit 6
	rm /etc/shadow.new || exit 7

	# set proper permissions on /etc/shadow!
	chmod 0640 /etc/shadow || exit 7

	# device nodes

	# This is required for Funtoo udev prior to 135-r8 only.
	
	echo "Creating device nodes..."
	[ -e /lib/udev/devices/ttyp0 ] || mknod /lib/udev/devices/ttyp0 c 3 0 || exit 8
	[ -e /lib/udev/devices/ptyp0 ] || mknod /lib/udev/devices/ptyp0 c 2 0 || exit 9
	[ -e /lib/udev/devices/ptmx ] || mknod /lib/udev/devices/ptmx c 5 2 || exit 10
	[ -e /lib/udev/devices/urandom ] || mknod /lib/udev/devices/urandom c 1 9 || exit 10
	[ -e /lib/udev/devices/random ] || mknod /lib/udev/devices/random c 1 8 || exit 10
	[ -e /lib/udev/devices/zero ] || mknod /lib/udev/devices/zero c 1 5 || exit 10

	# OpenRC - prior to 0.3.0
	# cp /etc/rc.conf /etc/rc.conf.orig || exit 11
	# cat /etc/rc.conf.orig | sed -e "/^#rc_devices/c\\" -e 'rc_devices="static"' > /etc/rc.conf || exit 12

	# timezone
	echo "Setting time zone..."
	rm -f /etc/localtime
	ln -s /usr/share/zoneinfo/UTC /etc/localtime || exit 13

	# sshd
	echo "Adding sshd to default runlevel..."
	rc-update add sshd default

	echo "Removing unnecessary udev stuff from default runlevel..."
	rc-update del udev-mount sysinit
	rc-update del udevd sysinit

	#hostname - change periods from target/name into dashes
	echo "Setting hostname..."
	myhost=`echo $[target/name] | tr . -`
	cat > /etc/conf.d/hostname << EOF || exit 14
# /etc/conf.d/hostname

# Set to the hostname of this machine
hostname=${myhost}
EOF

	#motd
	echo "Creating motd..."
	cat > /etc/motd << "EOF"
$[[files/motd]]
EOF
	rm -rf /etc/ssh/ssh_host* /var/tmp/* /var/log/* /tmp/* /root/.bash_history /etc/resolv.conf


	echo "Setting system type to OpenVZ..."
	echo 'rc_sys="openvz"' >> /etc/rc.conf

	# TESTS
	echo "Performing QA checks..."
	# root password blank
	[ "`cat /etc/shadow | grep ^root | cut -b1-7`" != 'root:!:' ] && exit 15
	echo "Root password check: PASSED"
	# tty must exist
	[ ! -e /dev/tty ] && exit 16
	echo "/dev/tty check: PASSED"
	echo "OpenVZ script complete."
]

[section files]

motd: [

 >>> OpenVZ Template:               $[target/name]
 >>> Version:                       $[target/version]
 >>> Created by:                    $[local/author]

 >>> Send suggestions, improvements, bug reports relating to...

 >>> This OpenVZ template:          $[local/author]
 >>> Funtoo Linux (general):        Funtoo Linux (http://www.funtoo.org)
 >>> Gentoo Linux (general):        Gentoo Linux (http://www.gentoo.org)
 >>> OpenVZ (general):              OpenVZ (http://www.openvz.org)

 NOTE: This message can be removed by deleting /etc/motd.

]

