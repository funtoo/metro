[collect ./source/stage3.spec]
[collect ./target/stage4.spec]
[collect ./steps/capture/tar.spec]

[section stage4]

target/name: selinux-stage3

[section steps]

unpack/post: [
#!/bin/bash
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
# Temporary workaround for issue:
echo "app-admin/rsyslog ssl openssl" >> /etc/portage/package.use
# Another temporary workaround:
sed -i -e '/harmless/s/#.*//g' /var/git/meta-repo/kits/security-kit/sys-process/audit/audit-2.8.5-r1.ebuild || exit 9000
for pkg in selinux-base selinux-base-policy rsyslog postfix; do
	emerge $eopts $pkg || exit 2
done
for service in rsyslog auditd; do
	rc-update add $service default || exit 3
done
# This should be done last so it can override any default configs from packages emerged above:
if [ -e /tmp/fsroot.mtree ]; then
	emerge mtree || exit 1
	echo "Applying fsroot permissions/ownership..."
	mtree -U -f /tmp/fsroot.mtree -p /
fi
]
