metro/class: stage
ROOT: /tmp/stage1root
source: stage3
target: stage1 
sourceversion: $[lastdate]

chroot/pythonjunk: [
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
		bidx = buildpkgs.index(portage.dep_getkey(pkgs[idx]))
		buildpkgs[bidx] = pkgs[idx]
		if buildpkgs[bidx][0:1] == "*":
			buildpkgs[bidx] = buildpkgs[bidx][1:]
	except: pass

for b in buildpkgs: print b,
print
]

chroot/run: [
>> chroot/setup

cat > /tmp/build.py << EOF
>> chroot/pythonjunk
EOF

export buildpkgs="$(python /tmp/build.py)"
export STAGE1_USE="$(portageq envvar STAGE1_USE)"
export USE="-* bindist build ${STAGE1_USE}"
export FEATURES="$FEATURES nodoc noman noinfo"
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

export ROOT="$[ROOT]"
install -d $[ROOT]
#emerge baselayout || exit 1
emerge --noreplace --oneshot $[emerge/options] ${buildpkgs} || exit 1
]
