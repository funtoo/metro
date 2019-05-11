[collect ./source/stage2.spec]
[collect ./target/stage3.spec]
[collect ./steps/capture/tar.spec]

[section steps]

chroot/run: [
#!/bin/bash
$[[steps/setup]]

# use python2 if available - if not available, assume we are OK with python3
a=$(eselect python list | sed -n -e '1d' -e 's/^.* \(python[23]\..\).*$/\1/g' -e '/python2/p')
# if python2 is available, "$a" should be set to something like "python2.6":
if [ "$a" != "" ]
then
	eselect python set $a
	eselect python cleanup
fi

emerge $eopts -u1 portage || exit 1
emerge $eopts -u1 --nodeps ego || exit 1
export USE="$[portage/USE] bindist"
# handle perl upgrades
perl-cleaner --modules || exit 1
emerge $eopts -e system || exit 1

# zap the world file and emerge packages
rm -f /var/lib/portage/world || exit 2
emerge $eopts $[emerge/packages/first:zap] || exit 1
emerge $eopts $[emerge/packages:zap] || exit 1

# add default runlevel services
services=""
services="$[baselayout/services:zap]"

for service in $services
do
	s=${service%%:*}
	l=${service##*:}
	[ "$l" == "$s" ] && l="default"
	if [ -e /etc/init.d/$service ]; then
		rc-update add $s ${l}
	fi
done

if [ -e /usr/share/eselect/modules/vi.eselect ] && [ -e /bin/busybox ]
then
	eselect vi set busybox
fi
$[[steps/chroot/run/extra:lax]]
]

[section portage]

ROOT: /
