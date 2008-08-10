#!/bin/bash

. /tmp/chroot-functions.sh
update_env_settings

if [ -n "${clst_DISTCC}" ]
then
	cleanup_distcc
fi

if [ -n "${clst_ICECREAM}" ]
then
	cleanup_icecream
fi
