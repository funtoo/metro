#!/bin/bash

. /tmp/chroot-functions.sh

update_env_settings

setup_myfeatures

# Setup the environment
export FEATURES="${clst_myfeatures} nodoc noman noinfo"

echo "Here is what we are using for bootstrap:"
/usr/portage/scripts/bootstrap.sh -p ${bootstrap_opts}

## START BUILD
/usr/portage/scripts/bootstrap.sh ${bootstrap_opts} || exit 1

