[section target]

arch: amd64

[section portage]

CFLAGS: -O2 -march=opteron-sse3 -pipe
CHOST: x86_64-pc-linux-gnu
HOSTUSE: mmx sse sse2 sse3 3dnow 3dnowext
