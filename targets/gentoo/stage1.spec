[collect ./source/seed.spec]
[collect ./target/stage1.spec]
[collect ./steps/capture/tar.spec]

[section portage]

ROOT: /tmp/stage1root

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

die() {
	echo $*
	exit 1
}

export ORIG_PKGDIR=$PKGDIR
export PKGDIR=$ORIG_PKGDIR/initial_root
# upgrade portage, if necessary, before we begin:
emerge -1u sys-apps/portage || die
emerge -1u --nodeps app-admin/ego || die

# update python
pyver=$[version/python]
pyver=${pyver:0:1}
# pyver is now set to major version of specified python in metro config. The version specified in
# metro config is the "default" version enabled for the system.

# when we have python3 as a default, we'll want to enable something like this (conditional):
#if [ "$pyver" == "2" ]; then
emerge -u =dev-lang/python-2*
#fi
emerge -u =dev-lang/python-3* || die
latest_python3=$(eselect python list --python3 | sed -ne '/python/s/.*\(python.*\)$/\1/p' | sort | tail -n 1)
latest_python3=python-${latest_python3:6:3}
oldest_python3=$(eselect python list --python3 | sed -ne '/python/s/.*\(python.*\)$/\1/p' | sort | head -n 1)
oldest_python3=python-${oldest_python3:6:3}
if [ "$latest_python3" != "$oldest_python3" ]; then
	emerge -C =dev-lang/${oldest_python3}* || die
fi
# switch to correct python
eselect python set python$[version/python] || die
eselect python cleanup
emerge -1 --nodeps ego portage
ego sync --config-only

# FL-1398 update perl before we begin and try to update perl modules, if any installed/or will be installed.
# THIS IS A HACK and should be removed eventually. See FL-5220:
emerge -1 openssl openssh || die
emerge -u --nodeps $eopts perl || die
perl-cleaner --all -- $eopts || die
emerge $eopts -uDN world || die

cat > /tmp/build.py << "EOF"
$[[files/pythonjunk]]
EOF

export buildpkgs="$(python /tmp/build.py) dev-vcs/git"

# The following code should also be used in targets/gentoo/stage2.spec
export PYTHON_ABIS="$(portageq envvar PYTHON_ABIS)"
export FEATURES="$FEATURES nodoc noman noinfo"
export ROOT="$[portage/ROOT]"
ego profile mix-in +stage1 || die

# In some cases permissions of the root directory are incorrect, force them to 755
chmod 755 /

## Sanity check profile
if [ -z "${buildpkgs}" ]
then
	echo "Your profile seems to be broken."
	echo "Could not build a list of build packages."
	echo "Double check your profile settings and the 'packages' files."
	exit 1
else
	echo "WE ARE BUILDING: ${buildpkgs}"
fi
export PKGDIR=$ORIG_PKGDIR/new_root
install -d ${ROOT}

# It's important to merge baselayout first so it can set perms on key dirs
emerge $eopts --nodeps baselayout || exit 1

emerge $eopts -p -v --noreplace --oneshot ${buildpkgs} || exit 3
emerge $eopts --noreplace --oneshot ${buildpkgs} || exit 1

install -d ${ROOT}/{proc,sys,dev}
ego profile mix-in -stage1 || die
]
