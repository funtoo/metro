[collect $[path/metro]/specs/ports/funtoo.spec]

[section target]

arch: x86

[section portage]

CFLAGS: -O2 -march=pentium4 -pipe
CHOST: i686-pc-linux-gnu
HOSTUSE: mmx sse sse2
