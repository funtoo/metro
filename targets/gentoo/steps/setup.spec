[section steps]

#[option parse/lax]

setup: [
/usr/sbin/env-update
gcc-config 1
source /etc/profile
export MAKEOPTS="$[portage/MAKEOPTS:zap]"
export FEATURES="$[portage/FEATURES:zap]"
export EMERGE_WARNING_DELAY=0
export CLEAN_DELAY=0
export EBEEP_IGNORE=0
export EPAUSE_IGNORE=0
export CONFIG_PROTECT="-* /etc/locale.gen"
if [ -d /var/tmp/cache/compiler ]
then
	if ! [ -e /usr/bin/ccache ] 
	then
		emerge --oneshot --nodeps ccache || exit 2
	fi
	export CCACHE_DIR=/var/tmp/cache/compiler
	export FEATURES="$FEATURES ccache"
	/usr/bin/ccache -M 1G
	# The ccache ebuild has a bug where it will install links in /usr/lib/ccache/bin to reflect the current setting of CHOST.
	# But the current setting of CHOST may not reflect the current compiler available (remember, CHOST can be overridden in /etc/make.conf)

	# This causes problems with ebuilds (such as ncurses) who may find an "i686-pc-linux-gnu-gcc" symlink in /usr/lib/ccache/bin and
	# assume that an "i686-pc-linux-gnu-gcc" compiler is actually installed, when we really have an i486-pc-linux-gnu-gcc compiler
	# installed. For some reason, ncurses ends up looking for the compiler in /usr/bin and it fails - no compiler found.

	# It's a weird problem but the next few ccache-config lines takes care of it by removing bogus ccache symlinks and installing
	# valid ones that reflect the compiler that is actually installed on the system - so if ncurses sees an "i686-pc-linux-gnu-gcc"
	# in /usr/lib/ccache/bin, it looks for (and finds)  a real i686-pc-linux-gnu-gcc installed in /usr/bin.

	# I am including these detailed notes so that people are aware of the issue and so we can look for a more elegant solution to
	# this problem in the future. This problem crops up when you are using an i486-pc-linux-gnu CHOST stage3 to create an
	# i686-pc-linux-gnu CHOST stage1. It will probably crop up whenever the CHOST gets changed. For now, it's fixed :)

	if [ -e /usr/bin/ccache-config ]
	then
		for x in i386 i486 i586 i686 x86_64
		do
			ccache-config --remove-links $x-pc-linux-gnu
		done
		gccprofile="`gcc-config -c`"
		if [ $? -eq 0 ]
		then
			gccchost=`gcc-config -S $gccprofile | cut -f1 -d" "`
			echo "Setting ccache links to: $gccchost"
			ccache-config --install-links $gccchost
		else
			echo "There was an error using gcc-config. Ccache not enabled."
			unset CCACHE_DIR
			export FEATURES="$FEATURES -ccache"
		fi
	fi
fi
if [ -e /var/tmp/cache/package ]
then
	export PKGDIR=/var/tmp/cache/package
	eopts="$[emerge/options] --usepkg"
	export FEATURES="$FEATURES buildpkg"
else
	eopts="$[emerge/options]"
fi
# work around glibc sandbox issues:
FEATURES="$FEATURES -sandbox"
# the quotes below prevent variable expansion of anything inside make.conf
cat > /etc/make.conf << "EOF"
$[[files/make.conf]]
EOF
if [ "$[portage/files/package.use?]" = "yes" ]
then
cat > /etc/portage/package.use << "EOF"
$[[portage/files/package.use:lax]]
EOF
fi
if [ "$[portage/files/package.keywords?]" = "yes" ]
then
cat > /etc/portage/package.keywords << "EOF"
$[[portage/files/package.keywords:lax]]
EOF
fi
if [ "$[portage/files/package.unmask?]" = "yes" ]
then
cat > /etc/portage/package.unmask << "EOF"
$[[portage/files/package.unmask:lax]]
EOF
fi
if [ "$[portage/files/package.mask?]" = "yes" ]
then
cat > /etc/portage/package.mask << "EOF"
$[[portage/files/package.mask:lax]]
EOF
fi
if [ -d /var/tmp/cache/probe ]
then
$[[probe/setup:lax]]
fi
]

#[option parse/strict]
