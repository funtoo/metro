[collect $[path/metro]/subarch/$[build/subarch].spec]

[section metro]

class: stage

[section target]

type: stage
subarch: $[portage/stable]$[build/subarch]
name: gentoo-openvz-$[target/subarch]-$[target/version]

[section source]

: gentoo/stage3
name: stage3-$[source/subarch]-$[source/version]
version: $[target/version]
subarch: $[target/subarch]

[section path]

chroot: $[path/work]

[section steps]

unpack: [
#!/bin/bash
[ ! -d $[path/chroot] ] && install -d $[path/chroot] 
[ ! -d $[path/chroot]/tmp ] && install -d $[path/chroot]/tmp --mode=1777 || exit 2
if [ -e /usr/bin/pbzip2 ]
then
	echo "Extracting source stage $[path/mirror/source] using pbzip2..."
	pbzip2 -dc $[path/mirror/source] | tar xpf - -C $[path/chroot] || exit 3
else
	echo "Extracting source stage $[path/mirror/source]..."
	tar xjpf $[path/mirror/source] -C $[path/chroot] || exit 3
fi
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
tar czpf $[path/mirror/target] -C $[path/chroot] . 
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
	rm -f /etc/mtab
	ln -s /proc/mounts /etc/mtab || exit 1
	echo "proc /proc proc defaults 0 0" > /etc/fstab

	# turn off gettys
	mv /etc/inittab /etc/inittab.orig || exit 2
	cat /etc/inittab.orig | sed -e '/getty/s/^/#/' > /etc/inittab || exit 3
	rm -f /etc/inittab.orig || exit 4

	# reset root password
	cat /etc/shadow | sed -e 's/^root:[^:]*:/root:!:/' > /etc/shadow.new || exit 5
	cat /etc/shadow.new > /etc/shadow || exit 6
	rm /etc/shadow.new || exit 7

	# device nodes
	mknod /lib/udev/devices/ttyp0 c 3 0 || exit 8
	mknod /lib/udev/devices/ptyp0 c 2 0 || exit 9
	mknod /lib/udev/devices/ptmx c 5 2 || exit 10
	
	# OpenRC
	cp /etc/rc.conf /etc/rc.conf.orig || exit 11
	cat /etc/rc.conf.orig | sed -e "/^#rc_devices/c\\" -e 'rc_devices="static"' > /etc/rc.conf || exit 12
	
	# timezone
	rm /etc/localtime
	ln -s /usr/share/zoneinfo/UTC /etc/localtime || exit 13

	# sshd
	rc-update add sshd default

	#hostname - change periods from target/name into dashes
	myhost=`echo $[target/name] | tr . -`
	cat > /etc/conf.d/hostname << EOF || exit 14
# /etc/conf.d/hostname

# Set to the hostname of this machine
hostname=${myhost}
EOF

	#motd
	cat > /etc/motd << "EOF"
$[[files/motd]]
EOF
	rm -rf /etc/ssh/ssh_host* /var/tmp/* /var/log/* /tmp/* /root/.bash_history /etc/resolv.conf 

	# TESTS

	# root password blank
	[ "`cat /etc/shadow | grep ^root | cut -b1-7`" != 'root:!:' ] && exit 15
	# tty must exist
	[ ! -e /dev/tty ] && exit 16

	myvar=`cat $TMPDIR/etc/shadow | grep ^root | cut -b1-7`
	if [ "$myvar" != 'root:!:' ]
	then
		exit 17
	fi

]

[section files]

motd: [

 >>> OpenVZ Template:               $[target/name]
 >>> Version:                       $[target/version] 
 >>> Created by:                    $[local/author] 

 >>> Send suggestions, improvements, bug reports relating to... 
 
 >>> This OpenVZ template:          $[local/author]
 >>> Gentoo Linux (general):        Gentoo Linux (http://www.gentoo.org)
 >>> OpenVZ (general):              OpenVZ (http://www.openvz.org)

 Initial setup steps:
 1. nano /etc/resolv.conf, to set up nameservers
 2. set root password
 3. 'vzsplit'/'vzctl' to get/set resource usage (basic config bad for gentoo)
 4. 'emerge --sync' to retrieve a portage tree
 
 NOTE: This message can be removed by deleting /etc/motd.

]

