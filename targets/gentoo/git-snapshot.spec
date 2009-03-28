[section metro]

# This defines what internal Metro class is used to build this target
class: snapshot

[section target]

# a git-snapshot is a variant of a snapshot tarball that contains a full git repo, not just the bare files.
type: git-snapshot

[section steps]

run: [
#!/bin/bash

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
git checkout master || die "couldn't check out master branch"
git gc || die "couldn't gc"
echo "Creating $[path/mirror/snapshot]..."
install -d `dirname $[path/mirror/snapshot]` || die "Couldn't create output directory"
tarout="$[path/mirror/snapshot]"
tarout=${tarout%.*}
install -d $[path/work]
cp -a $[path/cache/git]/$[git/name] $[path/work]/portage
cd $[path/work]
tar cf $tarout portage || die "couldn't create git archive"
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
