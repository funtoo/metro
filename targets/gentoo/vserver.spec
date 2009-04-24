[collect $[path/metro]/subarch/$[target/subarch].spec]

[section metro]

class: chroot

[section target]

type: virtual-image
name: gentoo-vserver-$[target/subarch]-$[target/version]

[section source]

: gentoo/stage3
name: stage3-$[source/subarch]-$[source/version]
version: $[target/version]
subarch: $[target/subarch]

[section path/mirror]

source: $[:subpath]/$[source/name].tar.bz2
target: $[:subpath]/vserver/$[target/name].tar.bz2

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
tar cjpf $[path/mirror/target] -C $[path/chroot] .
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

	# default services
	services=""
	if [ "$[baselayout/services?]" = "yes" ]
	then
		services="$[baselayout/services:lax]"
	fi

	for service in $services
	do
		echo "Adding services to default runlevel..."
		rc-update add $service default
	done

	# cleanup
	rm -rf /etc/ssh/ssh_host* /var/tmp/* /var/log/* /tmp/* /root/.bash_history /etc/resolv.conf
]
