target: stage2
subarch: ~amd64

# stuff we specify - our info:
version: 2008.08.29 

# REQUIRED:
# RECOMMENDED, otherwise use HOSTUSE.
USE: $[HOSTUSE]
# arch stuff
arch: amd64
CFLAGS: -O2 -pipe
CHOST: x86_64-pc-linux-gnu
HOSTUSE: mmx sse sse2
profile: default/linux/$[arch]/2008.0

chroot/setup: [
	/usr/sbin/env-update
	source /etc/profile
	export EMERGE_WARNING_DELAY=0
	export CLEAN_DELAY=0
	export EBEEP_IGNORE=0
	export EPAUSE_IGNORE=0
	export CONFIG_PROTECT="-*"
	[ -d /var/tmp/ccache ] && export CCACHE_DIR=/var/tmp/ccache
]

chroot/files/locale.gen [
# /etc/locale.gen: list all of the locales you want to have on your system
#
# The format of each line:
# <locale> <charmap>
#
# Where <locale> is a locale located in /usr/share/i18n/locales/ and
# where <charmap> is a charmap located in /usr/share/i18n/charmaps/.
#
# All blank lines and lines starting with # are ignored.
#
# For the default list of supported combinations, see the file:
# /usr/share/i18n/SUPPORTED
#
# Whenever glibc is emerged, the locales listed here will be automatically
# rebuilt for you.  After updating this file, you can simply run `locale-gen`
# yourself instead of re-emerging glibc.

en_US ISO-8859-1
en_US.UTF-8 UTF-8
]

# do any cleanup that you need with things bind mounted here:

chroot/postrun: [
	$[chroot/setup]
	[ -e /var/tmp/ccache ] && emerge -C dev-util/ccache
[

# do the stuff here that you need to do, with bind mounts unmounted (for safety:)

chroot/clean: [
	rm -rf /etc/portage /etc/resolv.conf /var/tmp/* /tmp/* /root/* /usr/portage /var/log/*
]

chroot/run: [
	$[chroot/setup]
	/usr/portage/scripts/bootstrap.sh -p
	/usr/portage/scripts/bootstrap.sh || exit 1
]
