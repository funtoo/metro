[section target]

arch: x86

[section portage]

CFLAGS: -march=core2 -O2 -fomit-frame-pointer -pipe
CHOST: i686-pc-linux-gnu
HOSTUSE: mmx sse sse2
