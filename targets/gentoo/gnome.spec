[collect ./source/stage3.spec]
[collect ./target/stage4.spec]
[collect ./steps/stage.spec]
[collect ./steps/capture/tar.spec]

[section stage4]

target/name: gnome-stage3

[section target]

sys:

[section steps]

unpack/post: [
fsroot_loc=$[path/install]/etc/builds/$[target/build]/fsroot
if [ -d "$fsroot_loc" ]
	rsync -av "${fsroot_loc}/" "$[path/chroot]/" || exit 9
fi
if [ -e "${fsroot_loc}.mtree" ]; then
	cp "${fsroot_loc}.mtree" "$[path/chroot]/tmp/" || exit 10
fi
]

chroot/run: [
#!/bin/bash
$[[steps/setup]]
epro mix-in gnome gfxcard-nvidia gfxcard-amdgpu gfxcard-intel gfxcard-radeon || exit 1
epro flavor desktop || exit 2
emerge $eopts -uDN @world || exit 3
for pkg in gnome; do
	emerge $eopts $pkg || exit 4
done
]
