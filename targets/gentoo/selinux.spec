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
fsroot_loc=$[path/install]/etc/builds/$[target/build]/$[target]/fsroot
if [ -d "$fsroot_loc" ] && [ -e "${fsroot_loc}.mtree" ]; then
	install -d "$[path/chroot]/tmp/fsroot" || exit 8
	# we will need to sync this to the root filesystem after we're done merging...
	rsync -av "${fsroot_loc}/" "$[path/chroot]/tmp/fsroot" || exit 9
	cp "${fsroot_loc}.mtree" "$[path/chroot]/tmp/" || exit 10
else
	echo "ERROR: $fsroot_loc not found!"
	exit 1
fi
]

chroot/run: [
#!/bin/bash
#this is not working:
#export EGO_PROFILE_MIX_INS=selinux
$[[steps/setup]]
epro mix-in +selinux || exit 1
emerge $eopts -uDN @world || exit 1
# Temporary workaround for issue:
echo "app-admin/rsyslog ssl openssl" >> /etc/portage/package.use
for pkg in selinux-base selinux-base-policy rsyslog postfix; do
	emerge $eopts $pkg || exit 2
done
for service in rsyslog auditd; do
	rc-update add $service default || exit 3
done
# This should be done last so it can override any default configs from packages emerged above:
if [ -d /tmp/fsroot ]; then
	echo "Syncing custom config over myself..."
	rsync -av /tmp/fsroot/ / || exit 1
fi
if [ -e /tmp/fsroot.mtree ]; then
	emerge mtree || exit 1
	echo "Applying fsroot permissions/ownership..."
	mtree -U -f /tmp/fsroot.mtree -p /
fi
]
