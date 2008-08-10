#!/bin/bash

. /tmp/chroot-functions.sh

update_env_settings

setup_myfeatures

# Setup the build environment
export FEATURES="${clst_myfeatures}"
export USE="${USE} bindist ${clst_HOSTUSE}"

## START BUILD
# We need portage to be merged manually with USE="build" set to avoid frying
# our make.conf, otherwise, the system target could take care of it.

setup_portage

run_emerge "-e system"
rm -f /var/lib/portage/world
touch /var/lib/portage/world
