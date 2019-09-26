[collect ./source/stage3.spec]
[collect ./target/stage4.spec]
[collect ./steps/stage.spec]
[collect ./steps/capture/tar.spec]

[section stage4]

target/name: selinux-stage3

[section target]

sys:

[section steps]

unpack/post: [
# include:
# /etc/selinux/config
# /etc/fstab
# /etc/pam.d
# /etc/boot.conf
# others...
fsroot_loc=$[path/install]/etc/builds/$[target/build]/fsroot
if [ -d "$fsroot_loc" ] && [ -e "${fsroot_loc}.mtree" ]; then
	rsync -av "${fsroot_loc}/" "$[path/chroot]/" || exit 9
	cp "${fsroot_loc}.mtree" "$[path/chroot]/tmp/" || exit 10
fi
]

chroot/run: [
#!/bin/bash
export EGO_PROFILE_MIX_INS=selinux
$[[steps/setup]]
for service in rsyslogd auditd; do
	rc-update add $service default || exit 3
done
if [ -e /tmp/fsroot.mtree ]; then
	emerge mtree || exit 1
	echo "Applying fsroot permissions/ownership..."
	mtree -U -f /tmp/fsroot.mtree -p /
fi
for pkg in selinux-base selinux-base-policy rsyslog; do
	emerge $eopts $pkg || exit 2
done
]
