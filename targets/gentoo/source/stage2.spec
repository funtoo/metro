[collect ./common.spec]

[section source]

: stage2
name: $[]-$[:subarch]-$[:build]-$[:version]
build: $[target/build]
subarch: $[target/subarch]
version: $[target/version]
