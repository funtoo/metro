[collect ./stage/common.spec]
[collect ./stage/capture/tar.spec]

[section source]

: stage1
version: $[target/version]
subarch: $[target/subarch]
build: $[target/build]

[section target]

type: binary-image
name: $[target]-$[target/subarch]-$[target/version]

[section path/mirror]

source: $[:source/subpath]/stage1-$[source/subarch]-$[source/version].tar.bz2
target: $[:target/subpath]/$[target/name].tar.bz2

[section portage]

ROOT: /

[section steps]

chroot/run: [
#!/bin/bash
$[[steps/setup]]
export AUTOCLEAN="yes"
export CONFIG_PROTECT="-*"
export FEATURES="$FEATURES -collision-protect"

# For testing purposes only
export FEATURES="$FEATURES -sandbox"

cat > /tmp/bootstrap.py << "EOF"
$[[files/bootstrap.py]]
EOF
python /tmp/bootstrap.py --check || exit 1

USE="-* build bootstrap" emerge portage || exit 1

export USE="-* bootstrap `python /tmp/bootstrap.py --use`"
emerge $eopts `python /tmp/bootstrap.py --pkglist` || exit 1
emerge --clean || exit 1
emerge --prune sys-devel/gcc || exit 1

gcc-config $(gcc-config --get-current-profile)

# now, we need to do some house-cleaning... we may have just changed
# CHOSTS, which means we have some cruft lying around that needs cleaning
# up...

for prof in /etc/env.d/05gcc*
do
	TESTLDPATH=$(unset LDPATH; source $prof; echo $LDPATH)
	if [ ! -e $TESTLDPATH ]
	then
		echo 
		echo ">>>"
		echo ">>> Found old CHOST stuff... cleaning up..."
		echo ">>>"
		# this is an old gcc profile, so we'll do some cleaning:
		TESTCHOST=`basename $prof`
		TESTCHOST="${TESTCHOST/05gcc-/}"
		# ok, now TESTCHOST refers to our bogus CHOST, so we can do this:
		# remove bogus /usr/bin entries:
		rm -f /usr/bin/$TESTCHOST*
		rm -rf /usr/$TESTCHOST
		rm -f $prof
		rm -rf /etc/env.d/gcc/config-$TESTCHOST
	fi
done
# remove any remaining cruft in cached files...
env-update
]

[section files]

bootstrap.py: [
#!/usr/bin/python
import portage,sys
pkgdict={}
alloweduse=["nls", "bindist", "nptl", "nptlonly", "multilib", "userlocales" ]

use=portage.settings["USE"].split()

myuse=portage.settings["STAGE1_USE"].split()

for x in use:
	if x in alloweduse:
		myuse.append(x)
for dep in portage.settings.packages:
	if dep[0] == "*":
		dep = dep[1:]
	catpkg=portage.dep_getcpv(dep)
	split=portage.catpkgsplit(catpkg)
	if split != None:
		pkgdict[split[1]]=dep
	else:
		pkgdict[catpkg.split("/")[1]]=dep

pkglist = ["texinfo", "gettext", "binutils", "gcc", "glibc", "baselayout", "zlib" , "perl" ]

if "nls" not in use or "gettext" not in pkgdict.keys():
	pkglist.remove("gettext")

if not pkgdict.has_key("linux-headers"):
	pkgdict["linux-headers"]="virtual/os-headers"
if sys.argv[1] == "--check":
	if "build" in use or "bootstrap" in use:
		print "Error: please do not specify \"build\" or \"bootstrap\" in USE. Exiting."
		sys.exit(1)
	else:
		sys.exit(0)
elif sys.argv[1] == "--use":
	# TESTING NLS... not for production
	print "nls "+" ".join(myuse)
	sys.exit(0)
elif sys.argv[1] == "--pkglist":
	for x in pkglist:
		if pkgdict.has_key(x):
			print pkgdict[x],
	print
	sys.exit(0)
else:
	print sys.argv[0]+": invalid arguments: "+" ".join(sys.argv[1:])
	sys.exit(1)
]
