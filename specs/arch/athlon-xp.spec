[collect $[path/metro]/specs/ports/portage.spec]

[section target]

arch: x86

[section portage]

CFLAGS: -O2 -march=athlon-xp -pipe
CHOST: i686-pc-linux-gnu
HOSTUSE: mmx sse 3dnow
