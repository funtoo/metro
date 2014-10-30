[collect ./common.spec]

[section source]

: stage3
name: $[]-$[:subarch]-$[:build]-$[:version]
build: $[target/build]
arch_desc: $[target/arch_desc]
subarch: $[target/subarch]
version: << $[path/mirror/target/control]/version/stage3
