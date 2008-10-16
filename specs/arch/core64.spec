[collect $[path/metro]/specs/ports/gentoo.spec]

[section target]

arch: amd64

[section portage]

CFLAGS: -march=nocona -O2 -pipe
CHOST: x86_64-pc-linux-gnu
HOSTUSE: mmx sse sse2
