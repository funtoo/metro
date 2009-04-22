[section steps]

capture: [
#!/bin/bash
outdir=`dirname $[path/mirror/target]`
if [ ! -d $outdir ]
then
	install -d $outdir || exit 1
fi
tarout="$[path/mirror/target]"
tarout="${tarout%.*}"
tar cpf $tarout -C $[path/chroot/stage] .
if [ $? -ge 2 ]
then
	rm -f "$tarout" "$[path/mirror/target]"
	exit 1
fi	
if [ -e /usr/bin/pbzip2 ]
then
	pbzip2 -p4 $tarout
else
	bzip2 $tarout
fi
if [ $? -ne 0 ]
then
	echo "Compression error - aborting."
	rm -f $[path/mirror/target]
	exit 99
fi
]


