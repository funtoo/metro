[collect ./stage4-common.spec]

[section target]

pkgcache: $[target]
name: $[stage4/target/name]-$[:subarch]-$[:build]-$[:version]
name/latest: $[stage4/target/name]-$[path/mirror/link/suffix]
name/full_latest: $[stage4/target/name]-$[:subarch]-$[:build]-$[path/mirror/link/suffix]

