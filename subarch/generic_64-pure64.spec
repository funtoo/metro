[section target]

arch: amd64
arch_desc: pure64

[section portage]

CFLAGS: -mtune=generic -O2 -pipe
CHOST: x86_64-pc-linux-gnu
HOSTUSE: mmx sse sse2

