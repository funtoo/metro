# Common stuff used when actually building a snapshot

[collect ./global.spec]

[section target]

name: $[portage/name/full]

[section metro]

# This defines what internal Metro class is used to build this target
class: snapshot

[section target]

type: repository

[section path/mirror]

# "current" symlink:
link: $[:snapshot/subpath]/$[portage/name]-current.tar.bz2
link/dest: $[portage/name/full].tar.bz2

[section trigger]

ok/run: [
#!/bin/bash
# CREATE current symlink for the snapshot
rm -f $[path/mirror/link]
ln -s $[path/mirror/link/dest] $[path/mirror/link] || exit 3
]

[section steps]

# common/git/run is used for both the git-snapshot and snapshot targets
common/git/run: [

die() {
	rm -f $[path/mirror/snapshot] $tarout
	echo "$*"
	exit 1
}

# On keyboard interrupt, clean up our partially-completed file...
trap "die Removing incomplete $[path/mirror/snapshot]..." INT

! [ -d "$[path/cache/git]" ] && install -d "$[path/cache/git]"

if ! [ -e "$[path/cache/git]/$[git/name]" ]
then
	# create repo if it doesn't exist
	git clone $[git/remote] $[path/cache/git]/$[git/name] || die "Couldn't clone git repo"
fi
cd $[path/cache/git]/$[git/name] || die "Couldn't change directories to git repo"
branch=`git rev-parse --symbolic --branches | grep "^$[git/branch]"`
if [ "$branch" != "$[git/branch]" ]
then
	# create local branch since it doesn't exist yet
	git checkout --track -b $[git/branch] origin/$[git/branch] || die "Couldn't create local git branch"
else
	# otherwise, make sure the branch is active (so we can pull if necessary)
	git checkout $[git/branch] || die "Couldn't checkout local git branch"
fi
options="$[git/options]"
if [ "${options/pull/}" != "${options}" ]
then
	echo "Performing git pull..."
	# if we have the "pull" option in git/options, then make sure we're up-to-date
	git pull > /dev/null || die "Couldn't perform git pull"
fi
git checkout $[git/branch/tar] || die "couldn't check out branch $[git/branch/tar] for tarball"
git gc || die "couldn't gc"
echo "Creating $[path/mirror/snapshot]..."
install -d `dirname $[path/mirror/snapshot]` || die "Couldn't create output directory"
tarout="$[path/mirror/snapshot]"
tarout=${tarout%.*}
]

# common/git/pack is used for both the snapshot and git-snapshot targets
common/git/pack: [
if [ -e /usr/bin/pbzip2 ]
then
	echo "Compressing $tarout using pbzip2..."
	pbzip2 -p4 $tarout || die "Git pbzip2 failure"
else
	echo "Compressing $tarout using bzip2..."
	bzip2 $tarout || die "Git bzip2 failure"
fi
echo "Snapshot $[path/mirror/snapshot] created."


]

