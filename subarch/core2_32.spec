[section target]

arch: x86
arch_desc: x86-32bit

[section portage]

CFLAGS: -march=core2 -O2 -fomit-frame-pointer -pipe
CHOST: i686-pc-linux-gnu
HOSTUSE: mmx sse sse2 sse3 ssse3
