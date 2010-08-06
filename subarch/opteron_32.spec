[section target]

arch: x86

[section portage]

CFLAGS: -O2 -fomit-frame-pointer -march=opteron -pipe
CHOST: i686-pc-linux-gnu
HOSTUSE: mmx sse sse2 3dnow 3dnowext
