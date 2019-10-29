[collect ../snapshot/global.spec]
[collect ego.spec]

[section steps/unpack]

source: [
[ ! -d $[path/chroot] ] && install -d $[path/chroot]
[ ! -d $[path/chroot]/tmp ] && install -d $[path/chroot]/tmp --mode=1777
src="$[path/mirror/source]"
comp="${src##*.}"

if [ ! -e "$src" ]; then
	echo "Could not find uncompressed artifact $src..."
	src="${src%.*}"
	if [ -e "$src" ]; then
		echo "Found uncompressed artifact -- will use it."
	fi
fi

if [ ! -e "$src" ]; then
	echo "Source file $src not found, exiting."
	exit 200
fi
echo "Extracting source stage $src..."

# Perform the extraction:
tar -xp --exclude='./dev/*' -f "$src" -C $[path/chroot] || exit 3

# let's fix /lib if it is a problematic state. Note that this is NOT multilib-compatible.
if [ -d $[path/chroot]/lib ] && [ -d $[path/chroot]/lib64 ] && [ ! -h $[path/chroot]/lib ]; then
	echo "Attempting to fix split /lib..."
	# we have both /lib and /lib64 as regular directories. Need to fix. Sync everything to /lib.
	rsync -av $[path/chroot]/lib64/ $[path/chroot]/lib/ || exit 23
	# Now, remove lib64.
	rm -rf $[path/chroot]/lib64 || exit 24
	# Next, create a lib64 symlink pointing to /lib 
	ln -s /lib $[path/chroot]/lib64 || exit 25
	# we are done, but we are left with a wonky lib setup. This is actually backwards. It's easier to fix separately, below.
fi
if [ -h $[path/chroot]/lib64 ] && [ -d $[path/chroot]/lib ]; then
	# wonky lib setup. Let's fix. This can happen from previous step, or maybe we're just wonky.
	echo "Fixing wonky lib setup..."
	rm $[path/chroot]/lib64 || exit 29
	mv $[path/chroot]/lib $[path/chroot]/lib64 || exit 30
	ln -s /lib64 $[path/chroot]/lib || exit 31
fi
if [ -n "$(ls $[path/chroot]/lib.backup.* 2>/dev/null)" ]; then
	rm -rf $[path/chroot]/lib.backup.* || exit 26
fi

# let's fix /usr/lib if it is a problematic state. Note that this is NOT multilib-compatible.
if [ -d $[path/chroot]/usr/lib ] && [ -d $[path/chroot]/usr/lib64 ] && [ ! -h $[path/chroot]/usr/lib ]; then
	echo "Attempting to fix split /lib..."
	# we have both /lib and /lib64 as regular directories. Need to fix. Sync everything to /lib.
	rsync -av $[path/chroot]/usr/lib64/ $[path/chroot]/usr/lib/ || exit 23
	# Now, remove lib64.
	rm -rf $[path/chroot]/usr/lib64 || exit 24
	# Next, create a lib64 symlink pointing to /lib 
	ln -s /usr/lib $[path/chroot]/usr/lib64 || exit 25
	# we are done, but we are left with a wonky lib setup. This is actually backwards. It's easier to fix separately, below.
fi
if [ -h $[path/chroot]/usr/lib64 ] && [ -d $[path/chroot]/usr/lib ]; then
	# wonky lib setup. Let's fix. This can happen from previous step, or maybe we're just wonky.
	echo "Fixing wonky lib setup..."
	rm $[path/chroot]/usr/lib64 || exit 29
	mv $[path/chroot]/usr/lib $[path/chroot]/usr/lib64 || exit 30
	ln -s lib64 $[path/chroot]/usr/lib || exit 31
fi
if [ -n "$(ls $[path/chroot]/usr/lib.backup.* 2>/dev/null)" ]; then
	rm -rf $[path/chroot]/usr/lib.backup.* || exit 26
fi
]

snapshot: [
if [ "$[release/type]" == "official" ]; then
	snap="$(ls $[path/mirror/snapshot] )"

	[ ! -e "$snap" ] && echo "Required file $snap not found. Exiting" && exit 3

	scomp="${snap##*.}"
	if [ "$[snapshot/source/type]" == "meta-repo" ]; then
		outdir=/var/git
		[ ! -d $[path/chroot]/var/git ] && install -d $[path/chroot]/var/git --mode=0755
	else
		outdir=/usr
		[ ! -d $[path/chroot]/usr/portage ] && install -d $[path/chroot]/usr/portage --mode=0755
	fi

	echo "Extracting portage snapshot $snap..."

	case "$scomp" in
		bz2)
			if [ -e /usr/bin/pbzip2 ]
			then
				pbzip2 -dc "$snap" | tar xpf - -C $[path/chroot]$outdir || exit 4
			else
				tar xpf  "$snap" -C $[path/chroot]$outdir || exit 4
			fi
			;;
		gz|xz)
			tar xpf "$snap" -C $[path/chroot]$outdir || exit 4
			;;
		*)
			echo "Unrecognized source compression for $snap"
			exit 300
			;;
	esac
	if [ "$[snapshot/source/type]" == "git" ]; then
		# support for "live" git snapshot tarballs:
		if [ -e $[path/chroot]/usr/portage/.git ]
		then
			cd $[path/chroot]/usr/portage 
			git checkout $[snapshot/source/branch:lax] || exit 50
		fi
	fi
fi
install -d $[path/chroot]/etc/portage/make.profile
cat > $[path/chroot]/etc/portage/make.profile/parent << EOF
$[profile/arch:zap]
$[profile/subarch:zap]
$[profile/build:zap]
$[profile/flavor:zap]
EOF
$[[steps/ego/prep]]
		cat $[path/chroot]/etc/ego.conf
		ROOT=$[path/chroot] /root/ego/ego sync || exit 9
]

env: [
install -d $[path/chroot]/etc/portage
cat << "EOF" > $[path/chroot]/etc/env.d/99zzmetro || exit 6
$[[files/proxyenv]]
EOF
cat << "EOF" > $[path/chroot]/etc/locale.gen || exit 7
$[[files/locale.gen]]
EOF
for f in /etc/resolv.conf /etc/hosts
do
	if [ -e $f ]
	then
		respath=$[path/chroot]$f
		if [ -e $respath ]
		then
			echo "Backing up $respath..."
			cp $respath ${respath}.orig
			if [ $? -ne 0 ]
			then
				 echo "couldn't back up $respath" && exit 8
			fi
		fi
		echo "Copying $f to $respath..."
		cp $f $respath
		if [ $? -ne 0 ]
		then
			echo "couldn't copy $f into place"
			exit 9
		fi
	fi
done
]
