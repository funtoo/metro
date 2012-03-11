[section steps]

livecd: [
emerge $eopts --noreplace app-misc/livecd-tools net-dialup/mingetty net-misc/dhcpcd sys-apps/hwsetup || exit 1

# setup init scripts
rc-update del keymaps boot
rc-update del netmount default

rc-update add autoconfig default
rc-update add fixinittab default

# permit root login via ssh
if [ -e /etc/ssh/sshd_config ]
then
	sed -i -e 's:^#PermitRootLogin\ yes:PermitRootLogin\ yes:' \
		/etc/ssh/sshd_config
fi

# set timezone
rm -rf /etc/localtime
cp /usr/share/zoneinfo/UTC /etc/localtime || exit 1

# set the hostname
echo 'hostname=livecd' > /etc/conf.d/hostname
echo '127.0.0.1 livecd.local livecd localhost' > /etc/hosts.orig

# try to get a network address via dhcp
echo 'dhcpcd eth0' > /etc/ifup.eth0

# for hwsetup
mkdir -p /etc/sysconfig

# make sure we have the latest pci, usb and hotplug ids
[ -x /sbin/update-pciids ] && /sbin/update-pciids
[ -x /sbin/update-usbids ] && /sbin/update-usbids
[ -x /usr/sbin/update-pciids ] && /usr/sbin/update-pciids
[ -x /usr/sbin/update-usbids ] && /usr/sbin/update-usbids

if [ -d /usr/share/hwdata ]
then
	# If we have uncompressed pci and usb ids files, symlink them.
	[ -f /usr/share/misc/pci.ids ] && [ -f /usr/share/hwdata/pci.ids ] && \
		rm -f /usr/share/hwdata/pci.ids && ln -s /usr/share/misc/pci.ids \
		/usr/share/hwdata/pci.ids
	[ -f /usr/share/misc/usb.ids ] && [ -f /usr/share/hwdata/usb.ids ] && \
		rm -f /usr/share/hwdata/usb.ids && ln -s /usr/share/misc/usb.ids \
		/usr/share/hwdata/usb.ids
	# If we have compressed pci and usb files, we download our own copies.
	[ -f /usr/share/misc/pci.ids.gz ] && [ -f /usr/share/hwdata/pci.ids ] && \
		rm -f /usr/share/hwdata/pci.ids && wget -O /usr/share/hwdata/pci.ids \
		http://pciids.sourceforge.net/v2.2/pci.ids
	[ -f /usr/share/misc/usb.ids.gz ] && [ -f /usr/share/hwdata/usb.ids ] && \
		rm -f /usr/share/hwdata/usb.ids && wget -O /usr/share/hwdata/usb.ids \
		http://www.linux-usb.org/usb.ids
fi

# save some space
emerge --depclean || exit 1
rm -rf /usr/lib/debug || exit 1
]
