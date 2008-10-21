[section target]

: openvz
name: gentoo-openvz-$[target/subarch]-$[target/version]

[section source]

: stage3
name: $[]-$[source/subarch]-$[source/version]
version: $[target/version]
subarch: $[target/subarch]

[section openvz]

author: Daniel Robbins <drobbins@funtoo.org>

