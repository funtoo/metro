[collect ../steps/symlink.spec]
[collect ../steps/remote.spec]

[section target]

name: $[remote/target/name]-$[:subarch]-$[:build]-$[:version]
name/latest: $[remote/target/name]-$[path/mirror/link/suffix]
name/full_latest: $[remote/target/name]-$[:subarch]-$[:build]-$[path/mirror/link/suffix]
