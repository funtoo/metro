[collect ./source/stage2.spec]
[collect ./target/stage3.spec]
[collect ./steps/capture/tar.spec]

[section portage]

ROOT: /

[section steps]

chroot/run: [
#!/bin/bash
$[[steps/setup]]

# Use python2 if available - if not available, assume we are OK with python3
a=$(eselect python list | sed -n -e '1d' -e 's/^.* \(python[23]\..\).*$/\1/g' -e '/python2/p')

# If python2 is available, "${a}" should be set to something like "python2.6":
if [[ -n "${a}" ]]; then
	eselect python set ${a}
fi

# Emerge portage and the base system
export USE="bindist"
emerge ${eopts} -q portage || exit 1
emerge ${eopts} -e system || exit 1

# Removes the world file
rm -f /var/lib/portage/world || exit 2

# Add default runlevel services
unset services; services="$[baselayout/services:zap]"

# No point on wasting time running this for loop if the above line is zapped.
if [[ -n "${services}" ]]; then
	echo ""
	for service in ${services}; do
		s=${service%%:*}
		l=${service##*:}
		[[ "${l}" == "${s}" ]] && l="default"
		rc-update add ${s} ${l}
	done
	echo ""
fi

if [[ -e "/usr/share/eselect/modules/vi.eselect" ]] && [[ -e "/bin/busybox" ]]; then
	# Hides the following error message:
	# "Couldn't find a man page for busybox; skipping."
	eselect vi set busybox > /dev/null 2>&1
fi
]
