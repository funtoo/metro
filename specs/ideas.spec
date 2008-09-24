ideas on the metaprogramming/repo interface

version: 2008.08.29
subarch: ~amd64
emerge/options: --jobs=5 --load-average=5

# import - pull into existing namespace
%import spec /etc/metro/global.spec
# /etc/metro/global.spec would contain:
storedir/spec: $[storedir]/$[subarch]/funtoo-$[subarch]-$[version]/meta/metro.spec

%link repo specs /usr/lib/metro/specs atom [type]/[name].spec

target/globals: [
	%import spec /etc/metro/global.spec
	%import atom specs:arch/amd64
	%import atom specs:ports/funtoo
]	

target:stage: [
	<< target/globals
	%import atom specs:target/$[stage]
]

spec/storedir: 
spec/run: $[target]:stage1 $[target]:stage2 $[target]:stage3

# have metro generate a spec file, then run from the spec file.
# use multiple command-line arguments for multiple targets. Example:

metro --run snapshot stage1 stage2 stage3 << EOF
%link: [
	repo specs /usr/lib/metro/specs
]
%collect: [
	spec /etc/metro/global.spec
	atom specs:arch/amd64
	atom specs:ports/funtoo
	atom specs:targets/$[target]
	genf $[storedir/spec]
]
EOF

%link: [
	repo conf /etc/portage
	repo profile /etc/make.profile
	repo installed /var/db/pkg
	repo ports /usr/portage
]

# get $[version]

metro --eval "$[version]" [collection]

# metro takes one local spec, runs multiple times - each time it creates a new object and sets "target" to be the command-line supplied value


metro --eval "value" [collection]
# evaluate "value" using "specfile" - print output to stdout, return 0 on success, 1+ on failure

metro --run target1 [target2...] [collection]
# use specfile to run targets - if genf in spefile/collect, also generate spec files

metro 

metro --run stage3
metro --eval st

Usage: metro [--collection x] [--eval "string"] TARGET...

/etc/metro/collections/funtoo
/etc/metro/collections/default -> funtoo

funtoo:

metro/sharedir: /usr/lib/metro

