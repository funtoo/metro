[collect ./source/stage4.spec]
[collect ./target/stage4.spec]
[collect ./steps/capture/tar.spec]

[section portage]

ROOT: /

[section steps]

chroot/run: [
#!/bin/bash
$[[steps/setup]]

emerge ${eopts} -1uq portage || exit 1
export USE="$[portage/USE] bindist"
emerge ${eopts} --usepkg=n -uDN $[emerge/rpackages:zap] || exit 2
emerge ${eopts} -uDN @world || exit 2
emerge ${eopts} -uDN $[emerge/packages/force:zap] || exit 2
emerge ${eopts} -uDN $[emerge/packages:zap] || exit 2

if [[ "$(emerge --list-sets | grep preserved-rebuild)" == "preserved-rebuild" ]]; then
	emerge ${eopts} @preserved-rebuild || exit 3
fi

# Run perl-cleaner to ensure all modules rebuilt after a major perl update, fix FL-122
perl-cleaner --all || exit 4
]

