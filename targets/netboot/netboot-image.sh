#!/bin/bash

. /tmp/chroot-functions.sh

update_env_settings

echo "Copying files to ${clst_root_path}"
clst_files="/bin/busybox ${clst_files} "
for f in ${clst_files}
do 
	copy_file ${f}
done
echo "Done copying files"
