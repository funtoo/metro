#what what I want
metro/class: snapshot
target: snapshot

run/rsync: [
	tmpname=`dirname $[storedir/snapshot]`/.`basename $[storedir/snapshot]`
	rsync -a --delete --exclude /packages/ --exclude /distfiles/ --exclude /local/ --exclude CVS/ --exclude /.git/ $[snapshot/path]/ $[workdir]/portage/ || exit 1
	tar -cjf $tmpname -C $[workdir]/portage || exit 1
]

run/git: [
	tmpname=`dirname $[storedir/snapshot]`/.`basename $[storedir/snapshot]`
	{ cd $[snapshot/path] || exit 1; git checkout $[snapshot/branch] || exit 1; }
	{ cd $[snapshot/path] || exit 1; git archive --prefix=portage/ HEAD | gzip > $tmpname || exit 1; }
	mv $tmpanme $[storedir/snapshot] || exit 1
]


