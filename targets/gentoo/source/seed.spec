[collect ./common.spec]

# A stage1 is no longer considered a stage3 derivative, because it may use a
# "remote" (ie. not in the current build/subarch directory) stage3 as a seed.
# True stage3 derivatives use a stage3 that has the same build, subarch and
# version as the target.

[section source]

: stage3
name: $[]-$[:subarch]-$[:build]-$[:version]

# When building a stage1, we're always going to use a stage3 as a seed. If
# $[strategy/build] is "local", we'll grab a local stage3. If it's "remote",
# we're going to use a remote stage3. This collect annotation makes this
# happen:

[collect ./seed/strategy/$[strategy/build]]
