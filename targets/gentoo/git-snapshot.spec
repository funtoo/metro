# The "git-snapshot" target generates a "live" snapshot tarball, ie. one that
# is a fully-functioning git repository (with the .git directory intact.)

[collect ./snapshot/common.spec]

[section steps]

create: [
install -d $[path/work]
cp -a $[path/cache/git]/$[git/name] $[path/work]/portage
cd $[path/work]
tar cf $tarout portage || die "couldn't create git archive"
]

run: [
#!/bin/bash

# The "steps/common" steps below are defined in snapshot/common.spec and are used by
# both the snapshot and git-snapshot targets.

$[[steps/common/git/run]]
$[[steps/create]]
$[[steps/common/git/pack]]
]
