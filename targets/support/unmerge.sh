#!/bin/bash

source /tmp/chroot-functions.sh

update_env_settings

run_emerge -C ${clst_packages}

exit 0
