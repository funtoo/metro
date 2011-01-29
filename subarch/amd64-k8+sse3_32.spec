[section target]

arch: x86
arch_desc: x86-32bit

[section portage]

CFLAGS: -O2 -fomit-frame-pointer -march=k8-sse3 -pipe
CHOST: i686-pc-linux-gnu
HOSTUSE: mmx sse sse2 ssse3 3dnow 3dnowext
