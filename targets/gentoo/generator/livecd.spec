[section path/mirror]

generator: $[]/$[:generator/subpath]/$[generator/name].iso

[section generator]

: $[livecd/name]
name: $[]-$[:subarch]-$[:build]-$[:version]
build: $[target/build]
subarch: $[target/subarch]
version: << $[path/mirror/generator/control]/version/stage4/$[]
