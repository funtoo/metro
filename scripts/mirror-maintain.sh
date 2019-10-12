#!/bin/bash --login

# This script is meant to perform maintenance of the local mirror of metro builds. This script will clean up any old builds,
# and also call buildrepo digestgen to sign any new builds.

metro="$(dirname $0)/../metro"
buildrepo="$(dirname $0)/buildrepo"
mp="$($metro -k path/mirror 2>/dev/null)"
echo $mp
if [ -z "$mp" ]; then
	echo "Could not get path/mirror from metro configuration; exiting."
	exit 1
fi
$buildrepo clean | tee /tmp/foo.sh
echo
echo "About to perform the above clean actions in 5 seconds... (^C to abort...)"
for x in 5 4 3 2 1; do
	echo -n "$x "
	sleep 1
done
echo
sh /tmp/foo.sh
$buildrepo digestgen
