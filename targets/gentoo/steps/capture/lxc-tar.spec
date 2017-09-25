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
if [ ! -d $[path/lxc] ]
then
	install -d $[path/lxc]
fi
mv $[path/chroot/stage] $[path/lxc]/rootfs
metadata_yaml="$[path/lxc]/metadata.yaml"
case $[target/arch_desc] in
	x86-64bit)
		my_arch="x86_64"
		;;
	x86-32bit)
		my_arch="i686"
		;;
	*)
		my_arch="unknown"
		;;
esac
cat > ${metadata_yaml} << EOF
architecture: ${my_arch}
creation_date: $(date +%s)
EOF
cd $[path/lxc] && tar cpf $tarout --xattrs --acls *
if [ $? -ge 2 ]
then
	rm -f "$tarout" "$[path/mirror/target]"
	exit 1
fi
case "$[target/compression]" in
	bz2)
		if [ -e /usr/bin/pbzip2 ]
		then
			pbzip2 -p4 $tarout
		else
			bzip2 $tarout
		fi
		;;
	xz)
		if [ -e /usr/bin/pxz ]; then
			pxz $tarout
		else
			xz --threads=0 $tarout
		fi
		;;
	gz)
		gzip $tarout
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
