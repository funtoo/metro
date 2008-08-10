#!/bin/bash

. /tmp/chroot-functions.sh

update_env_settings

setup_myfeatures

# Setup the environment
export FEATURES="${clst_myfeatures}"

## START BUILD
setup_portage

echo "Bringing system up to date using profile specific use flags"
export USE="${USE} ${clst_HOSTUSE}"
run_emerge -u system

echo "Emerging packages using stage4 use flags"
if [ -n "${clst_use}" ]
then
	USE="${clst_HOSTUSE} ${clst_use}"
fi

run_emerge "${clst_packages}"
