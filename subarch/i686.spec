[section target]

arch: x86

[section portage]

CHOST: i686-pc-linux-gnu
HOSTUSE:

[when target/toolchain is 2008]

CFLAGS: -O2 -march=i686 -pipe

[when target/toolchain is 2009]

CFLAGS: -O2 -march=i686 -mtune=generic -pipe

