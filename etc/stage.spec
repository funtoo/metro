storedir/srcstage: $[storedir]/$[subarch]/funtoo-$[subarch]-$[sourceversion]/$[source]-$[subarch]-$[sourceversion].tar.bz2 
storedir/deststage: $[storedir]/$[subarch]/funtoo-$[subarch]-$[version]/$[target]-$[subarch]-$[version].tar.bz2 
lastdate: << $[storedir]/$[subarch]/.control/lastdate
profile: default/linux/$[arch]/2008.0
USE: $[HOSTUSE]

chroot/prerun: [
	rm -f /etc/make.profile
	ln -sf ../usr/portage/profiles/$[profile] /etc/make.profile
]

probe/outfile: /usr/portage/distfiles/probe/log

probe/bashrc: [
#!/bin/bash
SANDBOX_ON=0
install -d `dirname $[probe/outfile]`
if [ "\$EBUILD_PHASE" != "depend" ]
then 
	echo -n "\$P.\$EBUILD_PHASE -"  >> $[probe/outfile]
	# if there are less than 100 device nodes....
	if [ \`ls /dev | wc -l\` -lt 100 ]
	then
		{ cd /dev; find > $[probe/outfile].\$P.\$EBUILD_PHASE.log; }
		echo " *** TRUE *** - logged to $[probe/outfile].\$P.\$EBUILD_PHASE.log" >> $[probe/outfile]
	else
		echo " false " >> $[probe/outfile]
	fi
fi
SANDBOX_ON=1
]

chroot/probe: [
# This is a useful piece of code to debug various build issues. May add it as a "probes" feature
# in the future. I used it to find that baselayout-2.0.0 was totally frying /usr/lib/gcc if it
# was merged after gcc. Now fixed temporarily by forcing baselayout to merge first- zmedico is
# working on a correct fix.

             # debug GCC issue
install -d /etc/portage
cat << EOF > /etc/portage/bashrc
>> probe/bashrc
EOF
]

chroot/setup: [
	/usr/sbin/env-update
	gcc-config 1
	source /etc/profile
	export EMERGE_WARNING_DELAY=0
	export CLEAN_DELAY=0
	export EBEEP_IGNORE=0
	export EPAUSE_IGNORE=0
	export CONFIG_PROTECT="-* /etc/locale.gen"
	if [ -d /var/tmp/ccache ] 
	then
		! [ -e /usr/bin/ccache ] && emerge --oneshot --nodeps ccache
		export CCACHE_DIR=/var/tmp/ccache
		export FEATURES="ccache"
	fi
	>> chroot/probe

	if [ `emerge --help | grep "\--jobs"` != "" ]
	then
		# if we have the emerge/jobs option, then use it.
		export EMERGE_DEFAULT_OPTS="--jobs $[emerge/jobs]"
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


