
[section steps/chroot]

prerun: [
#!/bin/bash
rm -f /etc/make.profile
ln -sf ../usr/portage/profiles/$[portage/profile] /etc/make.profile || exit 1
echo "Set Portage profile to $[portage/profile]."
]

# do any cleanup that you need with things bind mounted here:

postrun: [
#!/bin/bash
if [ "$[target]" != "stage1" ] && [ -e /usr/bin/ccache ]
then
	emerge -C dev-util/ccache || exit 1
fi
emerge -C $[emerge/packages/clean:zap] || exit 2
cat <<EOF > /etc/os-release
ID=$[release/name/id:zap]
NAME="$[release/name:zap]"
PRETTY_NAME="$[release/name/pretty:zap]"
CPE_NAME="$[release/name/cpe:zap]"
VERSION="$[release/version:zap]"
VERSION_ID=$[release/version/id:zap]
ANSI_COLOR="$[release/color:zap]"
EOF
]

clean: [
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
rm -rf $ROOT/var/cache/edb/dep/*
rm -f $ROOT/etc/.pwd.lock
for x in passwd group shadow
do
	# install a backup, but make sure it is the same as the current file, so we
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
if [ ! -e $ROOT/etc/make.conf.example ]
then
	if [ -e $ROOT/usr/share/portage/config/make.conf.example ]
	then
		ln -s ../usr/share/portage/config/make.conf.example $ROOT/etc/make.conf.example || exit 6
	fi
fi
# locale-archive can be ~81 MB; this should shrink it to 2MB.
rm -f /usr/lib*/locale/locale-archive
locale-gen
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
