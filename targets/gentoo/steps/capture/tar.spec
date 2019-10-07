[section path/mirror]

target/basename: $[target/name].tar.$[target/compression]
target/latest: $[target/name/latest].tar.$[target/compression]
target/full_latest: $[target/name/full_latest].tar.$[target/compression]

[section steps]

capture: [
#!/bin/bash
outdir=`dirname $[path/mirror/target]`
if [ ! -d $outdir ]
then
	install -o $[path/mirror/owner] -g $[path/mirror/group] -m $[path/mirror/dirmode] -d $outdir || exit 1
fi
tarout="$[path/mirror/target]"
# remove compression suffix:
tarout="${tarout%.*}"
tar cpf $tarout --xattrs --acls -C $[path/chroot/stage] .
if [ $? -ge 2 ]
then
	echo "Error creating tarball."
	rm -f "$tarout" "$[path/mirror/target]"
	exit 1
fi
# cme = "compress me"
touch $tarout.cme
# Note: we used to compress here. We no longer do. We want that handled out-of-band
# for performance reasons.
chown $[path/mirror/owner]:$[path/mirror/group] "$tarout" "${tarout}.cme"
exit 0
]
