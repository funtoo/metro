[collect ./stage/common.spec]
[collect ./stage/capture/tar.spec]

# A stage1 is no longer considered a stage3 derivative, because it may use
# a "remote" (ie. not in the current build/subarch directory) stage3 as a seed.
# True stage3-derivatives use a stage3 that has the same build, subarch and
# version as the target.

[section source]

: stage3
name: $[]-$[:subarch]-$[:build]-$[:version]

# When building a stage1, we're always going to use a stage3 as a seed. If
# $[strategy/build] is "local", we'll grab a local stage3. If it's "remote",
# we're going to use a remote stage3. This collect annotation makes this
# happen: 

[collect ./stage1/strategy/$[strategy/build]]

[section path/mirror]

source: $[:source/subpath]/$[source/name].tar.*

[section target]

name: $[]-$[:subarch]-$[:build]-$[:version]

[section portage]

ROOT: /tmp/stage1root

[section path/mirror]

target: $[:target/subpath]/$[target/name].tar.$[target/compression]

[section files]

pythonjunk: [
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
		bidx = buildpkgs.index(portage.dep.Atom.getkey(pkgs[idx]))
		buildpkgs[bidx] = pkgs[idx]
		if buildpkgs[bidx][0:1] == "*":
			buildpkgs[bidx] = buildpkgs[bidx][1:]
	except: pass

for b in buildpkgs: print(b)


]

[section steps]

chroot/run: [
#!/bin/bash
$[[steps/setup]]

# update python if it is available
emerge -u python || die 
# switch to new python
eselect python update || die 
python-updater || die

cat > /tmp/build.py << "EOF"
$[[files/pythonjunk]]
EOF

# upgrade portage on stage3 if necessary, before we begin:
emerge -u sys-apps/portage || die

export buildpkgs="$(python /tmp/build.py)"
export STAGE1_USE="$(portageq envvar STAGE1_USE)"
export USE="-* bindist build xml ${STAGE1_USE}"
export FEATURES="$FEATURES nodoc noman noinfo"

# In some cases permissions of the root directory are false, force them to 755

chmod 755 /

## Sanity check profile
if [ -z "${buildpkgs}" ]
then
	echo "Your profile seems to be broken."
	echo "Could not build a list of build packages."
	echo "Double check your /etc/make.profile link and the 'packages' files."
	exit 1
else
	echo "WE ARE BUILDING: ${buildpkgs}"
fi

export ROOT="$[portage/ROOT]"
install -d ${ROOT}
#DEBUG:

echo "/etc/make.conf contains:"
cat /etc/make.conf
echo
echo "FEATURES is set to:"
echo "$FEATURES"
echo

# It's important to merge baselayout first so it can set perms on key dirs
emerge $eopts --nodeps baselayout || exit 1

echo "/etc/make.conf contains:"
cat /etc/make.conf
echo
echo "FEATURES is set to:"
echo "$FEATURES"
echo
echo "Portage version"
emerge --version
echo

emerge $eopts -p -v --noreplace --oneshot ${buildpkgs} || exit 3
emerge $eopts --noreplace --oneshot ${buildpkgs} || exit 1

# create minimal set of device nodes
install -d ${ROOT}/{proc,sys,dev/pts,dev/shm}

mknod() {
	echo "Creating device node $1"
	/bin/mknod $* || return 1
}

cd ${ROOT}/dev || die "Could not change directory to $2."

! [ -c console ] && rm -rf console
[ -e console ] || { mknod console c 5 1 && chmod 600 console; } || die

! [ -c null ] && rm -rf null
[ -e null ] || { mknod null c 1 3 && chmod 777 null; } || die

! [ -c tty ] && rm -rf tty
[ -e tty ] || { mknod tty c 5 0 && chmod 666 tty; } || die

! [ -c ttyp0 ] && rm -rf ttyp0
[ -e ttyp0 ] || { mknod ttyp0 c 3 0 && chmod 644 ttyp0; } || die

! [ -c ptyp0 ] && rm -rf ptyp0
[ -e ptyp0 ] || { mknod ptyp0 c 2 0 && chmod 644 ptyp0; } || die

! [ -c ptmx ] && rm -rf ptmx
[ -e ptmx ] || { mknod ptmx c 5 2 && chmod 666 ptmx; } || die

! [ -c urandom ] && rm -rf urandom
[ -e urandom ] || { mknod urandom c 1 9 && chmod 666 urandom; } || die

! [ -c random ] && rm -rf random
[ -e random ] || { mknod random c 1 8 && chmod 666 random; } || die

! [ -c zero ] && rm -rf zero
[ -e zero ] || { mknod zero c 1 5 && chmod 666 zero; } || die

! [ -c kmsg ] && rm -rf kmsg
[ -e kmsg ] || { mknod kmsg c 2 11 && chmod 600 kmsg; } || die

for x in 0 1 2 3
do
	# These devices are for initial serial console
	! [ -c ttyS${x} ] && rm -rf ttyS${x}
	[ -e ttyS${x} ] || { mknod ttyS${x} c 4 $(( 64 + $x )) && chmod 600 ttyS${x}; } || die
	# These devices are used for initial ttys - good to have
	! [ -c tty${x} ] && rm -rf tty${x}
	[ -e tty${x} ] || { mknod tty${x} c 4 $x && chmod 666 tty${x}; } || die

done

[ -d fd ] || ln -svf /proc/self/fd fd || die
[ -L stdin ] || ln -svf /proc/self/fd/1 stdin || die
[ -L stdout ] || ln -svf /proc/self/fd/1 stdout || die
[ -L stderr ] || ln -svf /proc/self/fd/2 stderr || die
[ -L core ] || ln -svf /proc/kcore core || die
]

[section trigger]

ok/run: [
#!/bin/bash

# Since we've completed a successful stage1 build, we will update our
# .control/version/stage1 file. This file records the version of the 
# last successful stage1 build.

install -d $[path/mirror/control]/version || exit 1
echo "$[target/version]" > $[path/mirror/control]/version/stage1 || exit 1

]
