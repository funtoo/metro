[collect ./common.spec]

[section source]

: stage2
name: $[]-$[:subarch]-$[:build]-$[:version]
version: $[target/version]
subarch: $[target/subarch]
build: $[target/build]
