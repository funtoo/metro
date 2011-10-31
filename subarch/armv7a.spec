[section target]

arch: arm
arch_desc: arm

[section portage]

CFLAGS: -O2 -pipe -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=hard
CHOST: armv7a-hardfloat-linux-gnueabi
HOSTUSE:
