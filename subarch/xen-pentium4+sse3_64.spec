[section target]

arch: amd64
arch_desc: x86-64bit

[section portage]

CHOST: x86_64-pc-linux-gnu
HOSTUSE: mmx sse sse2 ssse3
CFLAGS: -O2 -march=nocona -mno-tls-direct-seg-refs -pipe


