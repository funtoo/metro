[collect ./common.spec]

[section source]

: stage3
name: $[]-$[:subarch]-$[:build]-$[:version]
build: $[target/build]
subarch: $[target/subarch]
version: << $[path/mirror/target/control]/version/stage3
