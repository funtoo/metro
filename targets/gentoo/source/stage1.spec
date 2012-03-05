[collect ./common.spec]

[section source]

: stage1
name: $[]-$[:subarch]-$[:build]-$[:version]

# The collect annotation below will allow us to grab a remote stage1
# for our build if $[strategy/build] is "remote" and $[strategy/seed]
# is "stage1". In all other cases, we use a local stage1 as source.

[collect ./stage1/strategy/$[strategy/build]/$[strategy/seed]]
