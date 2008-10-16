[collect $[path/metro]/specs/ports/gentoo.spec]

[section target]

arch: x86

[section portage]

CFLAGS: -O2 -march=i686 -pipe
CHOST: i686-pc-linux-gnu
HOSTUSE: 
