[section target]

arch: amd64
arch_desc: pure64

[section portage]

CFLAGS: -O2 -march=k8 -pipe
CHOST: x86_64-pc-linux-gnu
HOSTUSE: mmx sse sse2 3dnow 3dnowext
