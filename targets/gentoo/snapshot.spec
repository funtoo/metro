# The "snapshot" target generates a "dead" snapshot tarball, ie. just a bunch
# of files, from either a remote rsync or filesystem location (when
# snapshot/type: rsync) or a git repository (when snapshot/type: git).

[collect ./snapshot/common.spec]

[section steps when snapshot/type is rsync]

run: [
#!/bin/bash
	rsync -a --delete --exclude /packages/ --exclude /distfiles/ --exclude /local/ --exclude CVS/ --exclude /.git/ $[rsync/path]/ $[path/work]/portage/ || exit 1
	tar -cjf $[path/mirror/snapshot] -C $[path/work] portage
	if [ $? -ne 0 ]
	then
		rm -f $[path/mirror/snapshot]
		exit 1
	fi
]

[section steps when snapshot/type is git]

create: [
	git archive --prefix=portage/ $[git/branch] > $tarout || die "Couldn't create git archive"
]

run: [
#!/bin/bash

# The "steps/common" steps below are defined in snapshot/common.spec and are used by
# both the snapshot and git-snapshot targets.

$[[steps/common/git/run]]
$[[steps/create]]
$[[steps/common/git/pack]]
]
