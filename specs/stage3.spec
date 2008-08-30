target: stage3

# stuff we specify - our info:
version: 2008.08.29 
lastdate: << $[storedir]/$[arch]/.control/lastdate
portname: funtoo

# REQUIRED:
subarch: ~amd64
# RECOMMENDED, otherwise use HOSTUSE.
USE: $[HOSTUSE]
# LOCATIONS
storedir: /home/mirror/linux
storedir/srcstage: $[storedir]/$[subarch]/$[portname]-$[lastdate]/$[source]-$[subarch]-$[lastdate].tar.bz2 
storedir/deststage: $[storedir]/$[subarch]/$[portname]-$[version]/$[target]-$[subarch]-$[version].tar.bz2 
storedir/snapshot: $[storedir]/snapshots/$[portname]-$[version].tar.bz2 


# config
workdir:
chrootdir: $[workdir]/chroot



# arch stuff
arch: amd64
CFLAGS: -O2 -pipe
CHOST: x86_64-pc-linux-gnu
HOSTUSE: mmx sse sse2
profile: default/linux/$[arch]/2008.0
