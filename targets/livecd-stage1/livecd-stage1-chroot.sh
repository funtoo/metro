#!/bin/bash

. /tmp/chroot-functions.sh

update_env_settings

setup_myfeatures

# Setup the environment

export FEATURES="${clst_myfeatures}"

## START BUILD
setup_portage

export USE="${clst_use}"

run_emerge "${clst_packages}"
