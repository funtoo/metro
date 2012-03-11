[collect ./common.spec]

[section source]

: $[stage4/source/name]
name: $[]-$[:subarch]-$[:build]-$[:version]
build: $[target/build]
subarch: $[target/subarch]
version: << $[path/mirror/control]/version/stage4/$[stage4/source/name]
