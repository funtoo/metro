# The "snapshot" target generates a live snapshot (when snapshot/type: live),
# i.e. one that is a fully-functioning git repository (with the .git directory
# intact), or a dead snapshot (when snapshot/type: dead), i.e. just a bunch of
# files, from either a remote rsync or filesystem location.

[collect ./snapshot/source/$[snapshot/source/type]]
[collect ./snapshot/type/$[snapshot/type]]
[collect ./snapshot/common.spec]
