target: stage1

# stuff we specify - our info:
version: 2008.08.29 
portdir: /root/git/funtoo-portage
portname: funtoo

# REQUIRED:
subarch: ~amd64
# RECOMMENDED, otherwise use HOSTUSE.
USE: $[HOSTUSE]

chroot/setup: [
	/usr/sbin/env-update
	source /etc/profile
	export EMERGE_WARNING_DELAY=0
	export CLEAN_DELAY=0
	export EBEEP_IGNORE=0
	export EPAUSE_IGNORE=0
	export CONFIG_PROTECT="-*"
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
	rm -f /var/lib/portage/world
	touch /var/lib/portage/world
	rm -f /var/log/emerge.log	
]

chroot/pythonjunk: [
#!/usr/bin/python

import os,portage

# this loads files from the profiles ...
# wrap it here to take care of the different
# ways portage handles stacked profiles
def scan_profile(file):
	return portage.stack_lists( [portage.grabfile_package(os.path.join(x, file)) for x in portage.settings.profiles], incremental=1);

# loaded the stacked packages / packages.build files
pkgs = scan_profile("packages")
buildpkgs = scan_profile("packages.build")

# go through the packages list and strip off all the
# crap to get just the <category>/<package> ... then
# search the buildpkg list for it ... if it's found,
# we replace the buildpkg item with the one in the
# system profile (it may have <,>,=,etc... operators
# and version numbers)

for idx in range(0, len(pkgs)):
	try:
		bidx = buildpkgs.index(portage.dep_getkey(pkgs[idx]))
		buildpkgs[bidx] = pkgs[idx]
		if buildpkgs[bidx][0:1] == "*":
			buildpkgs[bidx] = buildpkgs[bidx][1:]
	except: pass

for b in buildpkgs: print b,
print
]

chroot/run: [
$[chroot/setup]
if [ -d /var/tmp/ccache ] 
then
	export CCACHE_DIR=/var/tmp/ccache
	! [ -e /usr/bin/ccache ] && emerge --nodeps --oneshot dev-util/ccache
fi

cat > /tmp/build.py << EOF
$[chroot/pythonjunk]
EOF

export buildpkgs="$(python /tmp/build.py)"
export STAGE1_USE="$(portageq envvar STAGE1_USE)"
export USE="-* bindist build ${STAGE1_USE}"
export FEATURES="nodoc noman noinfo"

## Sanity check profile
if [ -z "${clst_buildpkgs}" ]
then
	echo "Your profile seems to be broken."
	echo "Could not build a list of build packages."
	echo "Double check your /etc/make.profile link and the 'packages' files."
	exit 1
fi

emerge baselayout
emerge --noreplace --oneshot ${clst_buildpkgs}

]
