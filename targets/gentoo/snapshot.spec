# The "snapshot" target generates a "dead" snapshot tarball, ie. just a bunch
# of files, from either a remote rsync or filesystem location (when
# snapshot/type: rsync) or a git repository (when snapshot/type: git).

[collect ./snapshot/common.spec]
[collect ./snapshot/type/$[snapshot/type]]
