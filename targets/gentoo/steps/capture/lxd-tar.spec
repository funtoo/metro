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

rm -rf $[path/lxd]
install -d $[path/lxd]
mv $[path/chroot/stage] $[path/lxd]/rootfs

install -d $[path/lxd]/templates
echo 'hostname="{{ container.name }}"' > $[path/lxd]/templates/hostname.tpl

metadata_yaml="$[path/lxd]/metadata.yaml"
case $[target/arch_desc] in
	x86-64bit)
		my_arch="x86_64"
		my_arch_desc="64bit"
		;;
	pure64)
		my_arch="x86_64"
		my_arch_desc="64bit"
		;;
	x86-32bit)
		my_arch="i686"
		my_arch_desc="32bit"
		;;
	arm-64bit)
		my_arch="aarch64"
		my_arch_desc="64bit"
		;;
	arm-32bit)
		my_arch="armv7l"
		my_arch_desc="32bit"
		;;
	*)
		my_arch="unknown"
		my_arch_desc=""
		;;
esac

build_name="$[target/build]"

first_letter="${build_name:0:1}"
first_letter="${first_letter^^}"
os_name="${build_name%%-*}"
os_name="${first_letter}${os_name:1}"

type_name="${build_name#*-}"
type_name="${type_name%%-*}"
first_letter="${type_name:0:1}"
first_letter="${first_letter^^}"
type_name="${first_letter}${type_name:1}"

variety_name="${build_name#*-*-}"
if [[ "${variety_name}" == "${build_name}" ]] ; then
	variety_name=""
else
	variety_name="[${variety_name}]"
fi

subarch_name="$[target/subarch]"
subarch_name="${subarch_name#*-}"
first_letter="${subarch_name:0:1}"
first_letter="${first_letter^^}"
subarch_name="${first_letter}${subarch_name:1}"

cat > ${metadata_yaml} << EOF
architecture: ${my_arch}
creation_date: $(date +%s)
properties:
  name: $[target/build]-$[target/arch_desc]-$[target/subarch]
  description: ${os_name} ${type_name} ${subarch_name} ${my_arch_desc} ${variety_name} $(date +%F)
templates:
  /etc/conf.d/hostname:
    when:
      - create
      - copy
    template: hostname.tpl
EOF

cd $[path/lxd] && tar cpf $tarout --xattrs --acls *
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

rm -rf $[path/lxd]
]
