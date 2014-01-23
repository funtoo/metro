[collect ../snapshot/global.spec]

[section steps/unpack]

source: [
[[ ! -d "$[path/chroot]" ]] && install -d $[path/chroot]
[[ ! -d "$[path/chroot]/tmp" ]] && install -d $[path/chroot]/tmp --mode=1777 || exit 2
src="$(ls $[path/mirror/source])"
comp="${src##*.}"

[[ ! -e "${src}" ]] && echo "[Metro] Source file ${src} not found, exiting." && exit 1

echo -e "[Metro] Extracting source stage ${src} ..."

# Attempt to perform decompression with multiple cores
case "${comp}" in
bz2)
	if [[ -e "/usr/bin/pbzip2" ]]; then
		pbzip2 -dc "${src}" | tar xpf - -C $[path/chroot] || exit 3
	else
		tar xpf "${src}" -C $[path/chroot] || exit 3
	fi
	;;
gz)
	if [[ -e "/usr/bin/pigz" ]]; then
		pigz -dc "${src}" | tar xpf - -C $[path/chroot] || exit 3
	else
		tar xpf "${src}" -C $[path/chroot] || exit 3
	fi
	;;
xz)
	if [[ -e "/usr/bin/pxz" ]]; then
		pxz -dc "${src}" | tar xpf - -C $[path/chroot] || exit 3
	else
		tar xpf "${src}" -C $[path/chroot] || exit 3
	fi
	;;
*)
	echo "[Metro] Unrecognized source compression for ${src}" && exit 1
	;;
esac
]

snapshot: [
snap="$(ls $[path/mirror/snapshot] )"

[[ ! -e "${snap}" ]] && echo "Required file ${snap} not found. Exiting" && exit 3

scomp="${snap##*.}"

[[ ! -d "$[path/chroot]/usr/portage" ]] && install -d $[path/chroot]/usr/portage --mode=0755

echo -e "[Metro] Extracting portage snapshot ${snap} ..."

case "${scomp}" in
bz2)
	if [[ -e "/usr/bin/pbzip2" ]]; then
		pbzip2 -dc "${snap}" | tar xpf - -C $[path/chroot]/usr || exit 4
	else
		tar xpf "${snap}" -C $[path/chroot]/usr || exit 4
	fi
	;;
gz)
	if [[ -e "/usr/bin/pigz" ]]; then
		pigz -dc "${snap}" | tar xpf - -C $[path/chroot]/usr || exit 4
	else
		tar xpf "${snap}" -C $[path/chroot]/usr || exit 4
	fi
	;;
xz)
	if [[ -e "/usr/bin/pxz" ]]; then
		pxz -dc "${snap}" | tar xpf - -C $[path/chroot]/usr || exit 4
	else
		tar xpf "${snap}" -C $[path/chroot]/usr || exit 4
	fi
	;;
*)
	echo "[Metro] Unrecognized source compression for ${snap}" && exit 1
	;;
esac

# support for "live" git snapshot tarballs:
if [[ -e "$[path/chroot]/usr/portage/.git" ]]; then
	( cd $[path/chroot]/usr/portage; git checkout $[snapshot/source/branch:lax] || exit 50 )
fi
]

env: [
install -d $[path/chroot]/etc/portage

if [ "$[profile/format]" = "new" ]; then
	cat > $[path/chroot]/etc/portage/make.conf <<- "EOF" || exit 5
	$[[files/make.conf.newprofile]]
	EOF
else
	cat > $[path/chroot]/etc/portage/make.conf <<- "EOF" || exit 5
	$[[files/make.conf.oldprofile]]
	EOF
fi

cat > $[path/chroot]/etc/env.d/99zzmetro <<- "EOF" || exit 6
$[[files/proxyenv]]
EOF

cat > $[path/chroot]/etc/locale.gen <<- "EOF" || exit 7
$[[files/locale.gen]]
EOF

for f in /etc/resolv.conf /etc/hosts; do
	if [[ -e "${f}" ]]; then
		respath="$[path/chroot]${f}"

		if [[ -e "${respath}" ]]; then
			echo "[Metro] Backing up ${respath}..."

			cp $respath ${respath}.orig

			if [[ $? -ne 0 ]]; then
				 echo "Couldn't back up ${respath}" && exit 8
			fi
		fi

		cp ${f} ${respath}

		if [[ $? -ne 0 ]]; then
			echo "[Metro] Couldn't copy ${f} into place" && exit 9
		fi
	fi
done
]
