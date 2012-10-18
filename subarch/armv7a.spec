[section target]

arch: arm
arch_desc: arm-32bit/armv7a

[section portage]

CFLAGS: -O2 -pipe -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=soft
CHOST: armv7a-unknown-linux-gnueabi
HOSTUSE:
