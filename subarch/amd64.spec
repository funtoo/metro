[section target]

arch: amd64

[section portage]

CHOST: x86_64-pc-linux-gnu
HOSTUSE: mmx sse sse2

[when target/toolchain is 2008]

CFLAGS: -O2 -pipe

[when target/toolchain is 2009]

CFLAGS: -O2 -mtune=generic -pipe


