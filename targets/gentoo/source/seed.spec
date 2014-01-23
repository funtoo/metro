[collect ./common.spec]

[section source]

: stage4
name: $[]-$[:subarch]-$[:build]-$[:version]-$[:count]
[collect ./seed/strategy/$[strategy/build]-$[strategy/model]]
