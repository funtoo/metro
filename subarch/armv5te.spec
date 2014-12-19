[section target]

arch: arm
arch_desc: arm-32bit

[section portage]

CFLAGS: -O2 -pipe -march=armv5te 
CHOST: armv5tel-softfloat-linux-gnueabi 
CHOST_OVERRIDE: $[:CHOST]
HOSTUSE:

