#!/bin/bash

. /tmp/chroot-functions.sh

update_env_settings

if [ -n "${clst_CCACHE}" ]
then
	run_emerge -C dev-util/ccache || exit 1
fi

rm -f /var/log/emerge.log
