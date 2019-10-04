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
tarout="${tarout%.*}"
tar cpf $tarout --xattrs --acls -C $[path/chroot/stage] .
if [ $? -ge 2 ]
then
	rm -f "$tarout" "$[path/mirror/target]"
	exit 1
fi	
case "$[target/compression]" in
	bz2)
		if [ -e /usr/bin/pbzip2 ]
		then
			pbzip2 -9 -p4 $tarout
		else
			bzip2 -9 $tarout
		fi
		;;
	xz)
		xz -9 --threads=0 $tarout
		;;
	gz)
		gzip -9 $tarout
		;;
esac
if [ $? -ne 0 ]
then
	echo "Compression error - aborting."
	rm -f $[path/mirror/target]
	exit 99
fi
chown $[path/mirror/owner]:$[path/mirror/group] $[path/mirror/target]
]
