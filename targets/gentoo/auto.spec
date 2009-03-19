[collect /etc/metro/auto/$[metro/auto].conf]

[section metro]

class: target

[section target]

type: script

[section steps]

run: [
#!/bin/bash
source /etc/profile

die() {
	echo $*
	exit 1
}
MAINARGS="metro/build: $[metro/build] $target/subarch: $SUBARCH target/version: $CURDATE"
CONTROL=`metro -k path/mirror/control $MAINARGS`
	metro $MAINARGS target: $x || die "$x fail: metro failure"
done
]
