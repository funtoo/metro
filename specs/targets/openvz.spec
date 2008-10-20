[collect $[path/metro]/specs/arch/$[target/subarch].spec]

[section target]

class: chroot

[section steps]

chroot/test: [
	# root password blank
	[ "`cat /etc/shadow | grep ^root | cut -b1-7`" != 'root:!:' ] && exit 1
	# tty must exist
	[ ! -e /dev/tty ] && exit 1
	# OpenRC static device setting check
	[ -e /etc/rc.conf ] && [ `cat /etc/rc.conf | [ `grep '$rc_devices="static"'` = 'rc_devices="static"' ] || exit 1
]

chroot/clean: [
	rm -f /etc/ssh/ssh_host* /var/tmp/* /var/log/* /tmp/* /root/.bash_history /etc/resolv.conf 
]

chroot/run: [
	# mounts
	rm -f /etc/mtab
	ln -s /proc/mounts /etc/mtab || exit 1
	echo "proc /proc proc defaults 0 0" > /etc/fstab

	# turn off gettys
	mv /etc/inittab /etc/inittab.orig || exit 1
	cat /etc/inittab.orig | sed -e '/getty/s/^/#/' > /etc/inittab || exit 1
	rm -f /etc/inittab.orig || exit 1

	# reset root password
	cat /etc/shadow | sed -e 's/^root:[^:]*:/root:!:/' > /etc/shadow.new || exit 1
	cat /etc/shadow.new > /etc/shadow || exit 1
	rm /etc/shadow.new || exit 1

	# device nodes
	mknod /lib/udev/devices/ttyp0 c 3 0 || exit 1
	mknod /lib/udev/devices/ptyp0 c 2 0 || exit 1
	mynod /lib/udev/devices/ptmx c 5 2 || exit 1
	
	# OpenRC
	rc-update del consolefont boot
	cp /etc/rc.conf /etc/rc.conf.orig || exit 1
	cat /etc/rc.conf.orig | sed -e "/^#rc_devices/c\\" -e 'rc_devices="static"' > /etc/rc.conf || exit 1
	
	# timezone
	rm /etc/localtime
	ln -s /usr/share/zoneinfo/UTC /etc/localtime

	#hostname - change periods from target/name into dashes
	myhost=`echo $[target/name] | tr . -`
	cat > /etc/conf.d/hostname << EOF
# /etc/conf.d/hostname

# Set to the hostname of this machine
hostname=${myhost}
EOF

	#motd
	cat > /etc/motd << "EOF"
>> chroot/files/motd
EOF
	fi
]

[section files]

motd: [

 >>> OpenVZ Template:               $[target/name]
 >>> Version:                       $[target/version] 
 >>> Created by:                    $[openvz/author] 
 >>> CFLAGS:                        $[portage/CFLAGS]

 >>> Send suggestions, improvements, bug reports relating to... 
 
 >>> This OpenVZ template:          $[openvz/author]
 >>> Gentoo Linux (general):        Gentoo Linux (http://www.gentoo.org)
 >>> OpenVZ (general):              OpenVZ (http://www.openvz.org)

 Initial setup steps:
 1. nano /etc/resolv.conf, to set up nameservers
 2. set root password
 3. 'vzsplit'/'vzctl' to get/set resource usage (basic config bad for gentoo)
 4. 'emerge --sync' to retrieve a portage tree
 
 NOTE: This message can be removed by deleting /etc/motd.

]

