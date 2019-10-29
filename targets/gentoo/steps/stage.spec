
[section steps]

#[option parse/lax]

setup: [
#!/bin/bash
ego sync --config-only
/usr/sbin/env-update
# This should switch to most recent compiler:
gcc_num=$(gcc-config -l | grep \\[ | wc -l)
if [ "$gcc_num" -ge 1 ]; then
	echo
else
	gcc_num=1
fi
gcc-config $gcc_num
source /etc/profile
export MAKEOPTS="$[portage/MAKEOPTS:zap]"
export FEATURES="$[portage/FEATURES:zap]"
export EMERGE_WARNING_DELAY=0
export CLEAN_DELAY=0
export EBEEP_IGNORE=0
export EPAUSE_IGNORE=0
export CONFIG_PROTECT="-* /etc/locale.gen /etc/ego.conf"
export UNINSTALL_IGNORE="/etc/portage/*"
export DISTDIR="/var/cache/portage/distfiles"
if [ "$[target]" != "stage1" ]; then
	mixins=""
	mixins=$[profile/mix-ins:zap] $EGO_PROFILE_MIX_INS
	for mixin in $mixins; do
		ego profile mix-in +$mixin || exit 98
	done
	for mixin in $mixins; do
		if [ -z "$(grep $mixin /etc/portage/make.profile/parent)" ]; then
			exit 99
		fi
	done
	cat /etc/portage/make.profile/parent
fi
if [ -e /etc/make.conf ]; then
	mkconf=/etc/make.conf
else
	mkconf=/etc/portage/make.conf
fi
cat > /tmp/epro_getarch.py << "EOF"
#!/usr/bin/python3

import sys
import json

lines = sys.stdin.readlines()
try:
    j = json.loads("".join(lines))
except ValueError:
    sys.exit(1)
if "arch" in j and len(j["arch"]):
    a = j["arch"][0]
    if "path" in a:
        print(a["path"])
        sys.exit(0)
sys.exit(1)
EOF
archdir="$(ego profile show-json | python3 /tmp/epro_getarch.py)"
echo "$archdir" > /tmp/archdir
if [ -n "$archdir" ] && [ -e "$archdir/toolchain-version" ]; then
	# We will use toolchain_version to set a sub-directory for binary packages. This way, bumping the
	# toolchain version in the profile forces metro to rebuild all binary packages -- which is what we
	# want when we have a new toolchain, to flush out old, now stable .tbz2 files.
	toolchain_version="$(cat $archdir/toolchain-version)"
fi
if [ -e /var/tmp/cache/package ]
then
	export PKGDIR=/var/tmp/cache/package
	if [ -n "$toolchain_version" ]; then
		export PKGDIR="$PKGDIR/$toolchain_version"
	fi
	eopts="$[emerge/options] --usepkg --buildpkg"
else
	eopts="$[emerge/options]"
fi
install -d /etc/portage
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

# define this if needed:
#prerun: [
#]
#

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
# make sure /root exists and has proper perms:
install -d /root -m0700
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
if [ -e $ROOT/etc/ego.conf ]; then
	# we have a custom sync_base_url set but we don't want it in released stages.
	sed -i -e '/^sync_base_url.*/d' $ROOT/etc/ego.conf
fi
if [ "${ROOT}" = "/" ]
then
	# remove our tweaked configuration files, restore originals.
	for f in /etc/profile.env /etc/csh.env /etc/env.d/99zzmetro
	do
		echo "Cleaning chroot: $f..."
		rm -f "$f" || exit 1
	done
	for f in /etc/resolv.conf /etc/hosts
	do
		[ -e "$f" ] && rm -f "$f"
		if [ -e "$f.orig" ]
		then
			mv -f "$f.orig" "$f" || exit 2
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

# locale-archive can be ~81 MB; this should shrink it to 2MB.
rm -f /usr/lib*/locale/locale-archive
locale-gen
rm -rf $ROOT/run/*
# clean up any crap in /dev
rm -rf $ROOT/dev/*
]

postclean: [
rm -rf $[portage/ROOT]/tmp/*
# remove any franken-chroot stuff:
rm -rf $ROOT/usr/local/bin/*
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
