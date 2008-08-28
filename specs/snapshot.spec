# what I want
portname: funtoo
portdir: /root/git/funtoo-portage
version: 2008.08.29
target: snapshot

# config
storedir: /home/mirror/linux
storedir/snapshot: $[storedir]/snapshots/$[portname]-$[version].tar.bz2
