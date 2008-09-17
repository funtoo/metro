# /etc/catalyst.conf
distdir: /usr/portage/distfiles
options: ccache
storedir: /home/mirror/linux
storedir/snapshot: $[storedir]/snapshots/$[portname]-$[version].tar.bz2
workdir: /var/tmp/catalyst/$[subarch]/$[version]/$[target]
chrootdir: $[workdir]/chroot
MAKEOPTS: -j3
