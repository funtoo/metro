storedir/srcstage: $[storedir]/$[subarch]/$[portname]-$[subarch]-$[lastdate]/$[source]-$[subarch]-$[lastdate].tar.bz2 
storedir/deststage: $[storedir]/$[subarch]/$[portname]-$[subarch]-$[version]/$[target]-$[subarch]-$[version].tar.bz2 
lastdate: << $[storedir]/$[arch]/.control/lastdate
profile: default/linux/$[arch]/2008.0
USE: $[HOSTUSE]

chroot/prerun: [
	rm -f /etc/make.profile
	ln -sf ../usr/portage/profiles/$[profile] /etc/make.profile
]

chroot/setup: [
	/usr/sbin/env-update
	source /etc/profile
	export EMERGE_WARNING_DELAY=0
	export CLEAN_DELAY=0
	export EBEEP_IGNORE=0
	export EPAUSE_IGNORE=0
	export CONFIG_PROTECT="-*"
	if [ -d /var/tmp/ccache ] 
	then
		! [ -e /usr/bin/ccache ] && emerge --oneshot --nodeps ccache
		export CCACHE_DIR=/var/tmp/ccache
		export FEATURES="ccache"
	fi
]

chroot/clean: [
	rm -rf /etc/portage /var/tmp/* /tmp/* /root/* /usr/portage /var/log/*
	rm -f /var/lib/portage/world
	touch /var/lib/portage/world
]

# do any cleanup that you need with things bind mounted here:

chroot/postrun: [
	>> chroot/setup
	if [ "$[target]" != "stage1" ] 
	then
		if [ -e /var/tmp/ccache ] 
		then
			emerge -C dev-util/ccache 
		fi
	fi
]

chroot/files/locale.gen: [
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


