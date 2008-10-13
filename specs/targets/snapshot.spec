#what what I want
[section target]

class: snapshot
#require: snapshot/type snapshot snapshot/path target/version target path/mirror/snapshot

run/rsync: [
	rsync -a --delete --exclude /packages/ --exclude /distfiles/ --exclude /local/ --exclude CVS/ --exclude /.git/ $[portage/path]/ $[path/work]/portage/ || exit 1
	tar -cjf $[path/mirror/snapshot] -C $[path/work]/portage
	if [ $? -ne 0 ]
	then
		rm -f $[path/mirror/snapshot]
		exit 1
	fi
]

run/git: [
#!/bin/bash
	cd $[path/work] || exit 1
	git clone $[target/path] portage || exit 1
	cd portage || exit 1
	if [ "`git branch | grep ^* | cut -f2 -d" "`" != "$[target/branch]" ]
	then
		echo "Local branch does not exist yet, Metro will create it..."
		git checkout --track -b $[target/branch] origin/$[target/branch] || exit 1
	fi
	git archive --prefix=portage/ HEAD | bzip2 > $[path/mirror/snapshot]
	if [ $? -ne 0 ]
	then
		rm -f $[path/mirror/snapshot]
		exit 1
	fi
]

[section portage]

name: $[target/name]
