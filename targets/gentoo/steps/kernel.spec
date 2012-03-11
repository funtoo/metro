[section steps/kernel]

build: [
echo > /etc/fstab || exit 1
emerge $eopts --noreplace sys-kernel/genkernel $[livecd/kernel/package] || exit 1
genkernel $[livecd/kernel/opts:lax] \
	--cachedir=/var/tmp/cache/kernel \
	--modulespackage=/var/tmp/cache/kernel/modules.tar.bz2 \
	--minkernpackage=/var/tmp/cache/kernel/kernel-initrd.tar.bz2 \
	all || exit 1
]

clean: [
emerge -C sys-kernel/genkernel $[livecd/kernel/package] || exit 1
rm -rf /usr/src/linux-* /usr/src/linux || exit 1
]
