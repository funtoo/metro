[section target]

arch: x86

[section portage]

CFLAGS: -O2 -fomit-frame-pointer -march=prescott -mno-tls-direct-seg-refs -pipe
CHOST: i686-pc-linux-gnu
HOSTUSE: mmx sse sse2 ssse3
