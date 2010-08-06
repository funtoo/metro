[section target]

arch: x86

[section portage]

CFLAGS: -O2 -fomit-frame-pointer -march=athlon-xp -pipe
CHOST: i686-pc-linux-gnu
HOSTUSE: mmx sse 3dnow
