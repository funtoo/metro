[collect ./source/seed.spec]
[collect ./target/stage1.spec]
[collect ./steps/capture/tar.spec]

[section portage]

ROOT: /tmp/stage1

[section files]

pythonjunk: [
#!/usr/bin/python

import os, portage

# This loads files from the profiles, wrap it here to take care
# of the different ways portage handles stacked profiles
def scan_profile(file):
	return portage.stack_lists( [portage.grabfile_package(os.path.join(x, file)) for x in portage.settings.profiles], incremental=1);

# Load the stacked packages / packages.build files
pkgs = scan_profile("packages")
buildpkgs = scan_profile("packages.build")

# Go through the packages list and strip off all the
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

# Set the terminal so we don't get error messages saying the following:
# tput: No value for $TERM and no -T specified
export TERM="xterm"

# Before we begin, upgrade portage in the stage3 if necessary
emerge ${eopts} -uq sys-apps/portage || exit 1

# Update python if it is available
emerge ${eopts} -uq python || exit 1

# Switch to the correct python version
echo ""
eselect python set python$[version/python] || exit 2
python-updater || exit 2
echo ""

cat > /tmp/build.py << "EOF"
$[[files/pythonjunk]]
EOF

export buildpkgs="$(python /tmp/build.py)"
export BOOTSTRAP_USE="$(portageq envvar BOOTSTRAP_USE)"

# Set at least one PYTHON_ABIS flag to satisfy REQUIRED_USE of sys-apps/portage.
export PYTHON_ABIS="$(portageq envvar PYTHON_ABIS | sed -e "s/.* //")"
export USE="-* bindist build xml ${BOOTSTRAP_USE} ssl threads"
export FEATURES="${FEATURES} nodoc noman noinfo"

# In some cases permissions of the root directory are false, force them to 755
chmod 755 /

# Do sanity checks on the profile
if [[ -z "${buildpkgs}" ]]; then
	echo "Your profile seems to be broken."
	echo "Could not build a list of build packages."
	echo "Double check your profile settings and the 'packages' files."
	exit 1
fi

# Set the root directory variable and create it
export ROOT="$[portage/ROOT]" && install -d ${ROOT}

# It's important to merge baselayout first so it can set perms on key dirs
emerge ${eopts} --nodeps baselayout || exit 3

# Install 'util-linux' so that we have our mount/umount in our stage1
# and then emerge the packages in the buildpkgs list
emerge ${eopts} -1 --noreplace util-linux ${buildpkgs} || exit 4

# Create the minimum amount of device nodes in ${ROOT}/dev
install -d ${ROOT}/{proc,sys,dev/pts,dev/shm}

mknod() {
	/bin/mknod $@ || return 1
}

cd ${ROOT}/dev || exit 8

[[ ! -c "console" ]] && rm -rf console
[[ -e "console" ]] || { mknod console c 5 1 && chmod 600 console; } || exit 5

[[ ! -c "null" ]] && rm -rf null
[[ -e "null" ]] || { mknod null c 1 3 && chmod 777 null; } || exit 5

[[ ! -c "tty" ]] && rm -rf tty
[[ -e "tty" ]] || { mknod tty c 5 0 && chmod 666 tty; } || exit 5

[[ ! -c "ttyp0" ]] && rm -rf ttyp0
[[ -e "ttyp0" ]] || { mknod ttyp0 c 3 0 && chmod 644 ttyp0; } || exit 5

[[ ! -c "ptyp0" ]] && rm -rf ptyp0
[[ -e "ptyp0" ]] || { mknod ptyp0 c 2 0 && chmod 644 ptyp0; } || exit 5

[[ ! -c "ptmx" ]] && rm -rf ptmx
[[ -e "ptmx" ]] || { mknod ptmx c 5 2 && chmod 666 ptmx; } || exit 5

[[ ! -c "urandom" ]] && rm -rf urandom
[[ -e "urandom" ]] || { mknod urandom c 1 9 && chmod 666 urandom; } || exit 5

[[ ! -c "random" ]] && rm -rf random
[[ -e "random" ]] || { mknod random c 1 8 && chmod 666 random; } || exit 5

[[ ! -c "zero" ]] && rm -rf zero
[[ -e "zero" ]] || { mknod zero c 1 5 && chmod 666 zero; } || exit 5

[[ ! -c "kmsg" ]] && rm -rf kmsg
[[ -e "kmsg" ]] || { mknod kmsg c 2 11 && chmod 600 kmsg; } || exit 5

[[ ! -c "full" ]] && rm -rf full
[[ -e "full" ]] || { mknod full c 1 7 && chmod 644 full; } || exit 5

install -d -m 1777 shm || exit 5

for x in 0 1 2 3; do
	# These devices are for initial serial console
	[[ ! -c "ttyS${x}" ]] && rm -rf ttyS${x}
	[[ -e "ttyS${x}" ]] || { mknod ttyS${x} c 4 $(( 64 + ${x} )) && chmod 600 ttyS${x}; } || exit 6

	# These devices are used for initial ttys - good to have
	[[ ! -c "tty${x}" ]] && rm -rf tty${x}
	[[ -e "tty${x}" ]] || { mknod tty${x} c 4 ${x} && chmod 666 tty${x}; } || exit 6
done

[[ -d fd ]] || ln -svf /proc/self/fd fd || exit 7
[[ -L stdin ]] || ln -svf /proc/self/fd/1 stdin || exit 7
[[ -L stdout ]] || ln -svf /proc/self/fd/1 stdout || exit 7
[[ -L stderr ]] || ln -svf /proc/self/fd/2 stderr || exit 7
[[ -L core ]] || ln -svf /proc/kcore core || exit 7
]
