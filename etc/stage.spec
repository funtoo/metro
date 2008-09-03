storedir/srcstage: $[storedir]/$[subarch]/$[portname]-$[subarch]-$[lastdate]/$[source]-$[subarch]-$[lastdate].tar.bz2 
storedir/deststage: $[storedir]/$[subarch]/$[portname]-$[subarch]-$[version]/$[target]-$[subarch]-$[version].tar.bz2 
lastdate: << $[storedir]/$[arch]/.control/lastdate
profile: default/linux/$[arch]/2008.0
chroot/prerun: [
	rm -f /etc/make.profile
	ln -sf ../usr/portage/profiles/$[profile] /etc/make.profile
]
