# Common stuff used when actually building a snapshot
[collect ./global.spec]

[section target]

name: $[portage/name/full]

# This defines what internal Metro class is used to build this target
class: snapshot

[section path/mirror]

# "latest" symlink:
link: $[]/$[:snapshot/subpath]/$[portage/name]-$[:link/suffix].tar.$[snapshot/compression]
link/dest: $[portage/name/full].tar.$[snapshot/compression]

[section trigger]

ok/run: [
#!/bin/bash
# CREATE latest symlink for the snapshot
ln -sf $[path/mirror/link/dest] $[path/mirror/link] || exit 3
]

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

$[[steps/sync]]

echo "Creating $[path/mirror/snapshot]..."
install -d `dirname $[path/mirror/snapshot]` || die "Couldn't create output directory"
tarout="$[path/mirror/snapshot]"
tarout=${tarout%.*}

$[[steps/create]]

echo "Compressing $tarout..."
case "$[snapshot/compression]" in
bz2)
	if [ -e /usr/bin/pbzip2 ]
	then
		pbzip2 -p4 $tarout || die "Snapshot pbzip2 failure"
	else
		bzip2 $tarout || die "Snapshot bzip2 failure"
	fi
	;;
gz)
	gzip -9 $tarout || die "Snapshot gzip failure"
	;;
xz)
	if [ -e /usr/bin/pxz ]; then
		/usr/bin/pxz $tarout || die "Snapshot pxz failure"
	else
		xz --threads=0 $tarout || die "Snapshot xz failure"
	fi
	;;
*)
	echo "Unrecognized compression format $[snapshot/compression] specified for snapshot."
	exit 1
	;;
esac
echo "Snapshot $[path/mirror/snapshot] created."
]
