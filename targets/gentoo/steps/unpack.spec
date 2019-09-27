[collect ../snapshot/global.spec]
[collect ego.spec]

[section steps/unpack]

source: [
[ ! -d $[path/chroot] ] && install -d $[path/chroot]
[ ! -d $[path/chroot]/tmp ] && install -d $[path/chroot]/tmp --mode=1777
src="$(ls $[path/mirror/source])"
comp="${src##*.}"

[ ! -e "$src" ] && echo "Source file $src not found, exiting." && exit 1
echo "Extracting source stage $src..."

case "$comp" in
	bz2)
		if [ -e /usr/bin/pbzip2 ]
		then
			# Use pbzip2 for multi-core acceleration
			pbzip2 -dc "$src" | tar -xp --exclude='./dev/*' -f - -C $[path/chroot] || exit 3
		else
			tar -xp --exclude='./dev/*' -f "$src" -C $[path/chroot] || exit 3
		fi
		;;
	gz|xz)
		tar -xp --exclude='./dev/*' -f "$src" -C $[path/chroot] || exit 3
		;;
	*)
		echo "Unrecognized source compression for $src"
		exit 1
		;;
esac
# let's fix /lib if it is a problematic state. Note that this is NOT multilib-compatible.
if [ -d $[path/chroot]/lib ] && [ -d $[path/chroot]/lib64 ] && [ ! -h $[path/chroot]/lib ]; then
	echo "Attempting to fix split /lib..."
	# we have both /lib and /lib64 as regular directories. Need to fix.
	rsync -av $[path/chroot]/lib/ $[path/chroot]/lib64/ || exit 23
	rm -rf $[path/chroot]/lib || exit 24
	ln -s /lib64 $[path/chroot]/lib || exit 25
fi
if [ -n "$(ls $[path/chroot]/lib.backup.*)" ]; then
	rm -rf $[path/chroot]/lib.backup.* || exit 26
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
			exit 1
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
cat << "EOF" > $[path/chroot]/etc/portage/make.conf || exit 5
$[[files/make.conf.subarchprofile]]
EOF
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
