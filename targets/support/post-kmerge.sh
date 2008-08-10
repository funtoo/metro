#!/bin/bash

. /tmp/chroot-functions.sh

update_env_settings

# Only run depscan.sh if modules exist
if [ -n "$(ls /lib/modules)" ]
then
	/sbin/depscan.sh
	find /lib/modules -name modules.dep -exec touch {} \;
fi
