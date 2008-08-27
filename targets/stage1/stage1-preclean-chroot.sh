#!/bin/bash

. /tmp/chroot-functions.sh

# Now, some finishing touches to initialize gcc-config....
unset ROOT

setup_gcc
setup_binutils

if [ -d /usr/share/zoneinfo ]
then
	# use UTC as default timezone
	rm -f /etc/localtime
	cp /usr/share/zoneinfo/UTC /etc/localtime
fi

if [ -n "${clst_CCACHE}" ]
then
	run_emerge -C dev-util/ccache || exit 1
fi
