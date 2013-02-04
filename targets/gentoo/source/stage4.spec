[collect ./common.spec]

[section source]

: $[stage4/source/name]
name: $[]-$[:subarch]-$[:build]-$[:version]
build: $[target/build]
subarch: $[target/subarch]
version: << $[path/mirror/target/control]/version/stage4/$[]
