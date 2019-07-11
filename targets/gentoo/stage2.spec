[collect ./source/stage1.spec]
[collect ./target/stage2.spec]
[collect ./steps/capture/tar.spec]

[section portage]

ROOT: /

[section steps]

chroot/run: [
#!/bin/bash
$[[steps/setup]]
export AUTOCLEAN="yes"
export CONFIG_PROTECT="-*"
export FEATURES="$FEATURES -collision-protect"

ego profile mix-in +stage1
cat > /tmp/bootstrap.py << "EOF"
$[[files/bootstrap.py]]
EOF

export PYTHON_ABIS="$(portageq envvar PYTHON_ABIS)"
# this sets python targets to build even though we will be mangling USE soon...
# without this, python targets are all unset.
export PYTHON_TARGETS="$(portageq envvar PYTHON_TARGETS)"
export PYTHON_SINGLE_TARGET="$(portageq envvar PYTHON_SINGLE_TARGET)"

# set USE to expanded version of stage1 USE:
EXTRA_USE="$(python /tmp/bootstrap.py --use)"
ego profile mix-in +stage1
export USE="bootstrap $EXTRA_USE"

USE="-* build bootstrap" emerge portage || exit 1

# adding oneshot below so "libtool" doesn't get added to the world file... 
# libtool should be in the system profile, but is not currently there it seems.
echo
echo "USE is exported as: $USE"
echo
emerge $eopts --oneshot `python /tmp/bootstrap.py --pkglist` || exit 1
emerge --clean 
emerge --prune sys-devel/gcc || exit 1

# Currently, a minimal, barely functional Python is installed. Upgrade to
# a full-featured Python installation to avoid problems during the stage3
# build:

ego profile mix-in -stage1
for atom in `portageq match / dev-lang/python`
do
	emerge $eopts --oneshot =$atom || exit 1
done

gcc-config $(gcc-config --get-current-profile)

# remove any remaining cruft in cached files...
env-update
]

[section files]

bootstrap.py: [
#!/usr/bin/python
import portage,sys
pkgdict={}
alloweduse=["nls", "bindist", "nptl", "nptlonly", "multilib", "userlocales" ]
alloweduse_startswith = ["userland_"]

use=portage.settings["USE"].split()
myuse=[]
# expand USE variables using a limited subset of features that we should enable.

for x in use:
	if x in alloweduse:
		myuse.append(x)
	for y in alloweduse_startswith:
		if x.startswith(y):
			myuse.append(x)
			break

for dep in portage.settings.packages:
	if dep[0] == "*":
		dep = dep[1:]
	catpkg=portage.dep_getcpv(dep)
	split=portage.catpkgsplit(catpkg)
	if split != None:
		pkgdict[split[1]]=dep
	else:
		pkgdict[catpkg.split("/")[1]]=dep

pkglist = ["texinfo", "gettext", "binutils", "gcc", "glibc", "baselayout", "zlib", "shadow" ]

#, "perl", "python", "libtool" ]

# perl needs an interim remerge so it references the new CHOST in Config.pm, although this has been fixed in funtoo.
# python needs  a remerge so it references the new CHOST in its installed Makefile in /usr/lib/pythonx.y.
# libtool refernces the old CHOST so it seems like a good idea to remerge as well. This is all good stuff
# when we are using a non-native stage1. Not necessary when using a native stage1.

if "nls" not in use or "gettext" not in pkgdict.keys():
	pkglist.remove("gettext")
if not "linux-headers" in pkgdict:
	pkgdict["linux-headers"]="virtual/os-headers"
if sys.argv[1] == "--use":
	print("nls "+" ".join(myuse))
	sys.exit(0)
elif sys.argv[1] == "--pkglist":
	for x in pkglist:
		if x in pkgdict:
			sys.stdout.write(pkgdict[x]+" ")
	sys.stdout.write("\n")
	sys.exit(0)
else:
	print(sys.argv[0]+": invalid arguments: "+" ".join(sys.argv[1:]))
	sys.exit(1)
]
