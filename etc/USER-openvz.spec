[section target]

: openvz
name: gentoo-openvz-$[target/subarch]-$[target/version]

[section path/mirror]

dest: $[]/openvz/$[target/name].tar.gz
src: $[path/mirror/srcstage]

[section source]

: stage3
name: $[]-$[source/subarch]-$[source/version]
version: $[target/version]
subarch: $[target/subarch]

[section openvz]

author: Daniel Robbins <drobbins@funtoo.org>

