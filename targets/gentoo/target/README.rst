Target Specifications
=====================

Target specifications define the target type, version, subarch, build name and
the location of the target archive. The following target types exist:

stage1
------

This target is used to build a stage1 and is usually used together with the
seed source.  After a successful stage1 build, metro will update the
``.control/version/stage1`` file. This file records the version of the last
successful stage1 build.

stage2
------

This target is used to build a stage2 and is usually used together with the
stage1 source.

stage3
------

This target is used to build a stage3 and is usually used together with the
stage2 target. Not all stage3 targets are stage2 derivatives though.  A target
can be both a stage3 generator and a stage3 derivative -- stage3-freshen and
stage3-quick are two examples.

After a successful stage3 build, metro will update the
``.control/version/stage3`` file. This file records the version of the last
successful stage3 build.

stage4
------

This target is used to produce various specialized images such as preconfigured
webserver or database images and is usually used together with the stage3
source. It is also possible to build from a stage4 source in case the target is
just a superset of the source.

After each successful stage4 build, metro will update a file in the
``.control/version/stage4`` directory. This file records the version of the
last successful stage4 build.

container
---------

tbd
