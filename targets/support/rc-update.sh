#!/bin/bash

if [ "${clst_spec_prefix}" == "livecd" ]
then
	# default programs that we always want to start
	rc-update del iptables
	rc-update del netmount
	rc-update del keymaps
	rc-update del serial
	rc-update del consolefont
	rc-update add autoconfig default
	rc-update add modules boot
	rc-update add pwgen default
	[[ -e /etc/init.d/bootsplash ]] && rc-update add bootsplash default
	[[ -e /etc/init.d/splash ]] && rc-update add splash default
	[[ -e /etc/init.d/fbcondecor ]] && rc-update add fbcondecor default
	[[ -e /etc/init.d/sysklogd ]] && rc-update add sysklogd default
	[[ -e /etc/init.d/metalog ]] && rc-update add metalog default
	[[ -e /etc/init.d/syslog-ng ]] && rc-update add syslog-ng default

	# Do some livecd_type specific rc-update changes
	case ${clst_livecd_type} in
		gentoo-gamecd )
			rc-update add spind default
			;;
		gentoo-release-livecd )
			rc-update add spind default
			rc-update add xdm default
			;;
		generic-livecd )
			rc-update add spind default
			;;
		*)
			;;
	esac
fi

# Perform any rcadd then any rcdel
if [ -n "${clst_rcadd}" ] || [ -n "${clst_rcdel}" ]
then
	if [ -n "${clst_rcadd}" ]
	then
		for x in ${clst_rcadd}
		do
			echo "Adding ${x%%|*} to ${x##*|}"
			if [ ! -d /etc/runlevels/${x##*|} ]
			then
				echo "Runlevel ${x##*|} doesn't exist .... creating it"
				mkdir -p "/etc/runlevels/${x##*|}"
			fi
			rc-update add "${x%%|*}" "${x##*|}"
		done
	fi

	if [ -n "${clst_rcdel}" ]
	then
		for x in ${clst_rcdel}
		do
			rc-update del "${x%%|*}" "${x##*|}"
		done
	fi
fi

