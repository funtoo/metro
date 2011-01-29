[section target]

arch: amd64
arch_desc: x86-64bit

[section portage]

CFLAGS: -O2 -march=k8 -pipe
CHOST: x86_64-pc-linux-gnu
HOSTUSE: mmx sse sse2 3dnow 3dnowext
