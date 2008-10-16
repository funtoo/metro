[collect $[path/metro]/specs/ports/gentoo.spec]

[section target]

arch: x86

[section portage]

CFLAGS: -O2 -mtune=i686 -pipe
CHOST: i486-pc-linux-gnu
HOSTUSE: 
