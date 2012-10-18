[section target]

arch: arm
arch_desc: arm-32bit/armv6j_hardfp

[section portage]

CFLAGS: -O2 -pipe -march=armv6j -mfpu=vfp -mfloat-abi=hard
CHOST: armv6j-hardfloat-linux-gnueabi
HOSTUSE:
