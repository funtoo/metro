[collect ./epro.spec]

[section steps]

#[option parse/lax]

setup: [
# fix for bogus stages with buggy ego
sed -i -e /%s/d /etc/portage/make.profile/parent
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
export UNINSTALL_IGNORE="/etc/portage/*"
export DISTDIR="/var/cache/portage/distfiles"
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
if [ -e /etc/make.conf ]; then
	mkconf=/etc/make.conf
else
	mkconf=/etc/portage/make.conf
fi
$[[steps/epro_setup]]
if [ -e /var/tmp/cache/package ]
then
	export PKGDIR=/var/tmp/cache/package
	if [ -n "$toolchain_version" ]; then
		export PKGDIR="$PKGDIR/$toolchain_version"
	fi
	eopts="$[emerge/options] --usepkg"
	export FEATURES="$FEATURES buildpkg"
else
	eopts="$[emerge/options]"
fi
# work around glibc sandbox issues:
FEATURES="$FEATURES -sandbox"
install -d /etc/portage
# the quotes below prevent variable expansion of anything inside make.conf
if [ -n "$[profile/subarch]" ]; then
cat > $mkconf << "EOF"
$[[files/make.conf.subarchprofile]]
EOF
elif [ "$[profile/format]" = "new" ]; then
cat > $mkconf << "EOF"
$[[files/make.conf.newprofile]]
EOF
else
cat > $mkconf << "EOF"
$[[files/make.conf.oldprofile]]
EOF
fi
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
if [ "$[portage/files/package.accept_keywords?]" = "yes" ]
then
cat > /etc/portage/package.accept_keywords << "EOF"
$[[portage/files/package.accept_keywords:lax]]
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

clean: [
#!/bin/bash
# We do this in steps/clean instead of steps/chroot/clean because we have package
# cache bind-mount in /var/tmp. So we need to ensure it's unmounted first.
rm -rf $[path/chroot/stage]$[portage/ROOT]/var/tmp/*
]


[section steps/chroot]

prerun: [
#!/bin/bash
rm -f /etc/make.profile 
pf=""
pf=$[profile/format:zap]
if [ "$pf" = "new" ]; then
	# new-style profiles
	install -d /etc/portage/make.profile
	cat > /etc/portage/make.profile/parent << EOF
$[profile/arch:zap]
$[profile/subarch:zap]
$[profile/build:zap]
$[profile/flavor:zap]
EOF
	mixins=""
	mixins=$[profile/mix-ins:zap]
	for mixin in $mixins; do
		echo $mixin >> /etc/portage/make.profile/parent
	done
	if [ -d /var/git/meta-repo ]; then
		cd /var/git/meta-repo/kits/python-kit
		pykit="$(git branch --remote --verbose --no-abbrev --contains | sed -rne 's/^[^\/]*\/([^\ ]+).*$/\1/p' | grep -v HEAD)"
		cd /var/git/meta-repo/kits
		for kit in $(ls -d *kit); do
			ppath="/var/git/meta-repo/kits/$kit/profiles/funtoo/kits/python-kit/$pykit"
			[ -d "$ppath" ] && echo "$kit:funtoo/kits/python-kit/$pykit" >> /etc/portage/make.profile/parent
		done
	fi
	echo "New-style profile settings:"
	cat /etc/portage/make.profile/parent
else
	# classic profiles
	echo
	ln -sf ../usr/portage/profiles/$[portage/profile:zap] /etc/make.profile || exit 1
	echo "Set Portage profile to $[portage/profile:zap]."
fi
]

# do any cleanup that you need with things bind mounted here:

postrun: [
#!/bin/bash
if [ "$[target]" != "stage1" ] && [ -e /usr/bin/ccache ]
then
	emerge -C dev-util/ccache || exit 1
fi

emerge -C $[emerge/packages/clean:zap] || exit 2

# systemd compatible os-release file
cat <<EOF > /etc/os-release
ID="funtoo"
NAME="Funtoo GNU/Linux"
PRETTY_NAME="Linux"
VERSION="$[target/version:zap]"
VERSION_ID="$[target/subarch:zap]-$[target/version:zap]"
ANSI_COLOR="0;34"
HOME_URL="www.funtoo.org"
BUG_REPORT_URL="bugs.funtoo.org"
EOF

# motd
echo "Creating motd..."
cat > /etc/motd << "EOF"
$[[files/motd]]
EOF
]

clean: [
#!/bin/bash
# We only do this cleanup if ROOT = / - in other words, if we are going to be packing up /,
# then we need to remove the custom configuration we've done to /. If we are building a
# stage1, then everything is in /tmp/stage1root so we don't need to do this.
if [ -e /etc/make.conf ]; then
	mkconf=/etc/make.conf
else
	mkconf=/etc/portage/make.conf
fi
export ROOT=$[portage/ROOT]
if [ "${ROOT}" = "/" ]
then
	# remove our tweaked configuration files, restore originals.
	for f in /etc/profile.env /etc/csh.env /etc/env.d/99zzmetro
	do
		echo "Cleaning chroot: $f..."
		rm -f $f || exit 1
	done
	for f in /etc/resolv.conf /etc/hosts
	do
		[ -e $f ] && rm -f $f
		if [ -e $f.orig ]
		then
			mv -f $f.orig $f || exit 2
		fi
	done
else
	# stage1 - make sure we include our make.conf and profile link...
	pf=""
	pf="$[profile/format:zap]"
	rm -f $ROOT/etc/make.conf $ROOT/etc/portage/make.conf
	install -d $ROOT/etc/portage
	if [ "$pf" = "new" ]; then
		rm -f $ROOT/etc/portage/make.profile/parent || exit 3
		install -d $ROOT/etc/portage/make.profile
		cp -a /etc/portage/make.profile/parent $ROOT/etc/portage/make.profile/parent || exit 4
	else
		rm -f $ROOT/etc/make.profile || exit 3
		cp -a /etc/make.profile $ROOT/etc || exit 4
	fi
	cp $mkconf $ROOT/etc/portage/make.conf || exit 4
	ln -s portage/make.conf $ROOT/etc/make.conf
fi
# clean up temporary locations. Note that this also ends up removing our scripts, which
# exist in /tmp inside the chroot. So after this cleanup, any execution inside the chroot
# won't work. This is normally okay.

rm -rf $ROOT/tmp/* $ROOT/root/* $ROOT/var/git $ROOT/usr/portage $ROOT/var/log/* || exit 5
rm -rf $ROOT/var/cache/*
rm -f $ROOT/etc/.pwd.lock
for x in passwd group shadow
do
	# install a backup, but make sure it is the same as the latest file, so we
	# don't archive up any stale and potentially bad (personal password) info.
	rm -f $ROOT/etc/${x}-
	cp -a $ROOT/etc/${x} $ROOT/etc/${x}-
	chmod go-rwx $ROOT/etc/${x}-
done

rm -f $ROOT/etc/portage/bashrc

# for now, this takes care of glibc trying to overwrite locale.gen - clean up so
# users don't have etc-update bugging them:
find $ROOT/etc -iname '._cfg????_*' -exec rm -f {} \;

install -d $ROOT/etc/portage

# ensure that make.conf.example is set up OK...
if [ ! -e $ROOT/etc/portage/make.conf.example ] && [ ! -L $ROOT/etc/portage/make.conf.example ]
then
	if [ -e $ROOT/usr/share/portage/config/make.conf.example ]
	then
		ln -s ../../usr/share/portage/config/make.conf.example $ROOT/etc/portage/make.conf.example || exit 6
	fi
fi
# locale-archive can be ~81 MB; this should shrink it to 2MB.
rm -f /usr/lib*/locale/locale-archive
locale-gen
rm -rf $ROOT/run/*
]

postclean: [
rm -rf $[portage/ROOT]/tmp/*
]

test: [
#!/usr/bin/python
import os,sys,glob
from stat import *
from types import *

root="$[portage/ROOT]"

etcSecretFiles = [
	"/etc/default/useradd",
	"/etc/securetty",
	"/etc/ssh/sshd_config" ]

etcSecretGroupFiles = [
	"/etc/shadow" ]

etcSecretDirs = [
	"/etc/skel/.ssh",
	"/etc/ssl/private" ]

etcROFiles = [
	"/etc/passwd",
	"/etc/group" ]

abort=False

def goGlob(myglob):
	mylist = glob.glob(myglob)
	outlist = []
	for x in mylist:
		if not os.path.islink(x):
			outlist.append(x)
	return outlist

def fileCheck(files,perms,uid=0,gid=0):
	global abort
	if type(perms) == type("foo"):
		perms = [ perms ]
	# If a secret file exists, then ensure it has proper perms, otherwise abort
	for file in files:
		myfile = os.path.normpath(root+"/"+file)
		print(myfile)
		if os.path.exists(myfile):
			mystat = os.stat(myfile)
			myperms = "%o" % mystat[ST_MODE]
			myuid = mystat[ST_UID]
			mygid = mystat[ST_GID]
			if myperms not in perms:
				print("ERROR: file %s does not have proper perms: %s (should be one of %s)" % ( myfile, myperms, perms ))
				abort = True
			else:
				print("TEST: file %s OK" % myfile)
			if myuid != uid:
				print("ERROR: file %s does not have uid of %i" % ( myfile, uid ))
				abort = True
			if mygid != gid:
				print("ERROR: file %s does not have gid of %i" % ( myfile, gid ))
				abort = True


fileCheck(etcSecretFiles,"100600")
fileCheck(etcSecretGroupFiles,["100640","100600"])
fileCheck(etcSecretDirs,"40700")
fileCheck(etcROFiles,"100644")
fileCheck(goGlob("/etc/pam.d/*"),"100644")

if abort:
	sys.exit(1)
else:
	sys.exit(0)
]
