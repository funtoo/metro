[section target]

arch: sparc
arch_desc: sparc64

[section portage]

CFLAGS: -mcpu=niagara -O2 -fomit-frame-pointer -pipe
CHOST: sparc-unknown-linux-gnu
HOSTUSE:
