[collect ./stage/common.spec]
[collect ./stage/capture/tar.spec]
[collect ./stage/stage3-generator.spec]

[section path/mirror]

source: $[:source/subpath]/$[source/name].tar.*

[section source]

: stage2
name: $[]-$[:subarch]-$[:target]-$[:version]
version: $[target/version]
subarch: $[target/subarch]
build: $[target/build]

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
fi

USE="build" emerge --oneshot --nodeps portage || exit 1
export USE="$[portage/USE] bindist"
emerge $eopts -e system || exit 1

# zap the world file and emerge packages
rm -f /var/lib/portage/world || exit 2
if [ "$[emerge/packages?]" = "yes" ]
then
	emerge $eopts $[emerge/packages:lax] || exit 1
fi

# add default runlevel services
if [ "$[baselayout/services?]" = "yes" ]
then
	for service in $[baselayout/services:lax]
	do
		rc-update add $service default
	done
fi

if [ "$[metro/build]" = "funtoo" ] || [ "$[metro/build]" = "~funtoo" ]
then
	eselect vi set busybox
fi
]

[section portage]

ROOT: /
