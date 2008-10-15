[collect $[path/metro]/specs/ports/funtoo.spec]

[section target]

arch: amd64

[section portage]

CFLAGS: -O2 -pipe
CHOST: x86_64-pc-linux-gnu
HOSTUSE: mmx sse sse2
