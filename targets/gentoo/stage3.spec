[collect $[path/metro]/targets/gentoo/stage/main.spec]

[section steps]

chroot/run: [
#!/bin/bash
$[[steps/setup]]
USE="build" emerge --oneshot --nodeps portage || exit 1
export USE="$[portage/USE] bindist"
if [ -e /var/tmp/cache/package ]
then
	export PKGDIR=/var/tmp/cache/package
	eopts="$[emerge/options] --usepkg"
	export FEATURES="$FEATURES buildpkg"
else
	eopts="$[emerge/options]"
fi

emerge $eopts -e system || exit 1
# zap the world file...
rm -f /var/lib/portage/world || exit 2
if [ "$[emerge/packages?]" = "yes" ]
then
	emerge $eopts $[emerge/packages:lax] || exit 1
fi
]

[section portage]

ROOT: /


