#!/usr/bin/python

import os,portage,sys

# this loads files from the profiles ...
# wrap it here to take care of the different
# ways portage handles stacked profiles
# last case is for portage-2.1_pre*
def scan_profile(file):
	if "grab_stacked" in dir(portage):
		return portage.grab_stacked(file, portage.settings.profiles, portage.grabfile, incremental_lines=1);
	else:
		if "grab_multiple" in dir(portage):
			return portage.stack_lists( portage.grab_multiple(file, portage.settings.profiles, portage.grabfile), incremental=1);
		else:	
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

for b in buildpkgs: sys.stdout.write(b+" ")
