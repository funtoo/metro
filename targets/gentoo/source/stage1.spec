[collect ./common.spec]

[section source]

: stage1
name: $[]-$[:subarch]-$[:build]-$[:version]
[collect ./stage1/strategy/$[strategy/build]/$[strategy/seed]]
