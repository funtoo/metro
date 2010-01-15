[section steps]

chroot/prerun: [
#!/bin/bash
rm -f /etc/make.profile
ln -sf ../usr/portage/profiles/$[portage/profile] /etc/make.profile || exit 1
echo "Set Portage profile to $[portage/profile]."
]

#[option parse/lax]

setup: [
/usr/sbin/env-update
gcc-config 1
source /etc/profile
export MAKEOPTS="$[portage/MAKEOPTS]"
export EMERGE_WARNING_DELAY=0
export CLEAN_DELAY=0
export EBEEP_IGNORE=0
export EPAUSE_IGNORE=0
export CONFIG_PROTECT="-*"
if [ -d /var/tmp/cache/compiler ]
then
	if ! [ -e /usr/bin/ccache ] 
	then
		emerge --oneshot --nodeps ccache || exit 2
	fi
	export CCACHE_DIR=/var/tmp/cache/compiler
	export FEATURES="ccache"
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
			export FEATURES=""
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
if [ "$[portage/devices?]" = "yes" ]
then
	emerge --oneshot --nodeps sys-apps/makedev || exit 2
	MAKEDEV -d "$[portage/ROOT]/dev/" "$[portage/devices:lax]"
	emerge -C sys-apps/makedev
fi
if [ -d /var/tmp/cache/probe ]
then
$[[probe/setup:lax]]
fi
]

#[option parse/strict]

chroot/postclean: [
rm -rf $[portage/ROOT]/tmp/*
]

chroot/clean: [
#!/bin/bash
# We only do this cleanup if ROOT = / - in other words, if we are going to be packing up /,
# then we need to remove the custom configuration we've done to /. If we are building a
# stage1, then everything is in /tmp/stage1root so we don't need to do this.
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
	rm -f $ROOT/etc/make.conf $ROOT/etc/make.profile || exit 3
	cp -a /etc/make.conf /etc/make.profile $ROOT/etc || exit 4
fi
# clean up temporary locations. Note that this also ends up removing our scripts, which
# exist in /tmp inside the chroot. So after this cleanup, any execution inside the chroot
# won't work. This is normally okay.

rm -rf $ROOT/var/tmp/* $ROOT/tmp/* $ROOT/root/* $ROOT/usr/portage $ROOT/var/log/* || exit 5
rm -rf $ROOT/car/cache/edb/dep/*
rm -f $ROOT/etc/{passwd,group,shadow}- $ROOT/etc/.pwd.lock
rm -f $ROOT/etc/portage/bashrc
install -d $ROOT/etc/portage

# ensure that make.conf.example is set up OK...
if [ ! -e $ROOT/etc/make.conf.example ]
then
	if [ -e $ROOT/usr/share/portage/config/make.conf.example ]
	then
		ln -s ../usr/share/portage/config/make.conf.example $ROOT/etc/make.conf.example || exit 6
	fi
fi
]

# do any cleanup that you need with things bind mounted here:

chroot/postrun: [
#!/bin/bash
if [ "$[target]" != "stage1" ] && [ -e /usr/bin/ccache ]
then
	emerge -C dev-util/ccache || exit 1
fi
if [ "$[emerge/packages/clean?]" == "yes" ]
then
	emerge -C $[emerge/packages/clean:lax] || exit 2
fi
]

chroot/test: [
#!/usr/bin/python
import os,sys,glob
from stat import *

root="$[portage/ROOT]"

etcSecretFiles = [
	"/etc/default/useradd",
	"/etc/securetty",
	"/etc/shadow",
	"/etc/ssh/sshd_config" ]

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
	# If a secret file exists, then ensure it has proper perms, otherwise abort
	for file in files:
		myfile = os.path.normpath(root+"/"+file)
		if os.path.exists(myfile):
			mystat = os.stat(myfile)
			myperms = "%o" % mystat[ST_MODE]
			myuid = mystat[ST_UID]
			mygid = mystat[ST_GID]
			if myperms != perms:
				print "ERROR: file %s does not have proper perms: %s (should be %s)" % ( myfile, myperms, perms )
				abort = True
			else:
				print "TEST: file %s OK" % myfile
			if myuid != uid:
				print "ERROR: file %s does not have uid of %i" % ( myfile, uid )
				abort = True
			if mygid != gid:
				print "ERROR: file %s does not have gid of %i" % ( myfile, gid )
				abort = True


fileCheck(etcSecretFiles,"100600")
fileCheck(etcSecretDirs,"40700")
fileCheck(etcROFiles,"100644")
fileCheck(goGlob("/etc/pam.d/*"),"100644")

if abort:
	sys.exit(1)
else:
	sys.exit(0)

]

unpack: [
#!/bin/bash
[ ! -d $[path/chroot] ] && install -d $[path/chroot]
[ ! -d $[path/chroot]/tmp ] && install -d $[path/chroot]/tmp --mode=1777 || exit 2
echo -n "Extracting source stage $[path/mirror/source]"
if [ -e /usr/bin/pbzip2 ]
then
	echo " using pbzip2..."
	# Use pbzip2 for multi-core acceleration
	pbzip2 -dc $[path/mirror/source] | tar xpf - -C $[path/chroot] || exit 3
	[ ! -d $[path/chroot]/usr/portage ] && install -d $[path/chroot]/usr/portage --mode=0755
	echo "Extracting portage snapshot $[path/mirror/snapshot] using pbzip2..."
	pbzip2 -dc $[path/mirror/snapshot] | tar xpf - -C $[path/chroot]/usr || exit 4
else
	echo "..."
	tar xjpf $[path/mirror/source] -C $[path/chroot] || exit 3
	[ ! -d $[path/chroot]/usr/portage ] && install -d $[path/chroot]/usr/portage --mode=0755
	echo "Extracting portage snapshot $[path/mirror/snapshot]..."
	tar xjpf $[path/mirror/snapshot] -C $[path/chroot]/usr || exit 4
fi
# support for "live" git snapshot tarballs:
if [ -e $[path/chroot]/usr/portage/.git ]
then
	( cd $[path/chroot]/usr/portage; git checkout $[git/branch] || exit 50 )
fi
cat << "EOF" > $[path/chroot]/etc/make.conf || exit 5
$[[files/make.conf]]
EOF
cat << "EOF" > $[path/chroot]/etc/env.d/99zzmetro || exit 6
$[[files/proxyenv]]
EOF
cat << "EOF" > $[path/chroot]/etc/locale.gen || exit 7
$[[files/locale.gen]]
EOF
for f in /etc/resolv.conf /etc/hosts
do
	if [ -e $f ]
	then
		respath=$[path/chroot]$f
		if [ -e $respath ]
		then
			echo "Backing up $respath..."
			cp $respath ${respath}.orig
			if [ $? -ne 0 ]
			then
				 echo "couldn't back up $respath" && exit 8
			fi
		fi
		echo "Copying $f to $respath..."
		cp $f $respath
		if [ $? -ne 0 ]
		then
			echo "couldn't copy $f into place"
			exit 9
		fi
	fi
done
]
