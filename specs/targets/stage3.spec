[collect $[path/metro]/specs/arch/$[target/subarch].spec]
[collect $[path/metro]/etc/stage/files.conf]
[collect $[path/metro]/etc/stage/steps.conf]

[section target]

class: stage

[section steps]

run: [
#!/bin/bash
>> steps/setup
USE="build" emerge --oneshot --nodeps portage || exit 1
export USE="$[portage/USE] bindist"
emerge $[emerge/options] -e system || exit 1
if [ "$[emerge/packages]" != "" ]
then
	emerge $[emerge/options] $[emerge/packages] || exit 1
fi
]

[section portage]

ROOT: /


