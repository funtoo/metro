[section target]

arch: x86

[section portage]

CFLAGS: -O2 -fomit-frame-pointer -march=pentium4 -pipe
CHOST: i686-pc-linux-gnu
HOSTUSE: mmx sse sse2
