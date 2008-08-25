#!/bin/bash
. /tmp/chroot-functions.sh

update_env_settings

#setup_myfeatures

# Setup our environment
echo
echo "Output of /tmp/build.py:"
/tmp/build.py
echo

export clst_buildpkgs="$(/tmp/build.py)"
export STAGE1_USE="$(portageq envvar STAGE1_USE)"
export USE="-* bindist build ${STAGE1_USE}"
export FEATURES="${clst_myfeatures} nodoc noman noinfo"

## Sanity check profile
if [ -z "${clst_buildpkgs}" ]
then
	echo "Your profile seems to be broken."
	echo "Could not build a list of build packages."
	echo "Double check your /etc/make.profile link and the 'packages' files."
	exit 1
fi

## START BUILD
# emerge this first so we set up our /usr/lib dir correctly
run_emerge baselayout
run_emerge "--noreplace --oneshot ${clst_buildpkgs}"
rm -f /var/lib/portage/world
touch /var/lib/portage/world

rm -f /var/log/emerge.log
