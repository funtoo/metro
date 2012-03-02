[collect ./common.spec]

# This file defines common settings for all stage4 derivatives.  Stage4
# derivatives are those targets that are generated directly from a stage4, and
# include live media, ec2 and ova images.

[section source]

name: $[]-$[:subarch]-$[:build]-$[:version]

# When building from a stage4, we simply use the stage4 with matching
# build, subarch and version:

build: $[target/build]
subarch: $[target/subarch]
version: $[target/version]
