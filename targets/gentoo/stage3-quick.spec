[collect $[path/metro]/targets/gentoo/stage/main.spec]

[section steps]

chroot/run: [
#!/bin/bash
$[[steps/setup]]
emerge -u portage || exit 1
export ROOT=$[portage/ROOT]
export USE="$[portage/USE] bindist"
if [ -e /var/tmp/cache/package ]
then
	export PKGDIR=/var/tmp/cache/package
	eopts="$[emerge/options] --usepkg"
	export FEATURES="$FEATURES buildpkg"
else
	eopts="$[emerge/options]"
fi
emerge $eopts --nodeps sys-apps/baselayout || exit 1
emerge $eopts system || exit 1
# we are using a non-/ ROOT, so zapping the world file should not be necessary...
if [ "$[emerge/packages?]" = "yes" ]
then
	emerge $eopts $[emerge/packages:lax] || exit 1
fi
]

[section portage]

ROOT: /tmp/stage3root
