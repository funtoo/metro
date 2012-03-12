Source Specifications
=====================

Source specifications define the source type, version, subarch, build name and
the location of the source archive. The following source types exist:

seed
----

The seed source is usually used to build a stage1 target. A stage1 is not
considered a stage3 derivative, because it may use a *remote* stage3 as a seed
(ie. build and subarch do not match the target). True stage3 derivatives use a
stage3 that has the same build, subarch and version as the target.

When building a stage1, we're always going to use a stage3 as a seed though. If
``strategy/build`` is *local*, we'll grab a local stage3. If it's *remote*,
we're going to use a remote stage3.

stage1
------

The stage1 source is usually used to build a stage2 target. If
``strategy/build`` is *local*, we'll grab a local stage1. If it's *remote*,
we're going to use a remote stage1.

stage2
------

The stage2 source is usually used to build a stage3 target. Not all stage3
targets are stage2 derivatives though. A target can be both a stage3 generator
and a stage3 derivative -- stage3-freshen and stage3-quick are two examples.

stage3
------

The stage3 source is used for all stage3 derivatives. Stage3 derivatives are
those targets that are generated directly from a stage3, and include
stage3-freshen, stage3-quick, stage4, container or livecd media.

When building from a stage3, we simply use the stage3 with matching build,
subarch and version. To build from a different subarch/version use the seed
source. This is usually only done to build stage1 targets.

For a regular full build, the source/version and target/version will be
equal. However, for a stage3-freshen build, we will use the last-built
stage3 as a seed.

stage4
------

tbd
