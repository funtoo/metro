[collect ./common.spec]

[section source]

: stage2
name: $[]-$[:subarch]-$[:build]-$[:version]
build: $[target/build]
subarch: $[target/subarch]
arch_desc: $[target/arch_desc]
version: $[target/version]
