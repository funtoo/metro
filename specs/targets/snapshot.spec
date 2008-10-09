#what what I want
[section target]

class: snapshot
#require: snapshot/type snapshot snapshot/path target/version target path/mirror/snapshot

run/rsync: [
	tmpname=`dirname $[path/mirror/snapshot]`/.`basename $[path/mirror/snapshot]`
	rsync -a --delete --exclude /packages/ --exclude /distfiles/ --exclude /local/ --exclude CVS/ --exclude /.git/ $[portage/path]/ $[path/work]/portage/ || exit 1
	tar -cjf $tmpname -C $[path/work]/portage || exit 1
]

run/git: [
	if [ "$[portage/branch]" = "" ]
	then
		echo "snapshot/branch not defined. Please specify a branch."
		exit 1
	fi
	tmpname=`dirname $[path/mirror/snapshot]`/.`basename $[path/mirror/snapshot]`
	{ cd $[portage/path] || exit 1; git checkout $[path/mirror/snapshot] || exit 1; }
	{ cd $[portage/path] || exit 1; git archive --prefix=portage/ HEAD | gzip > $tmpname || exit 1; }
	mv $tmpanme $[path/mirror/snapshot] || exit 1
]


