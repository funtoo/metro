[section target]

arch: arm
arch_desc: arm-32bit/armv6j

[section portage]

CFLAGS: -O2 -pipe -march=armv6j -mfpu=vfp -mfloat-abi=soft
CHOST: armv6j-unknown-linux-gnueabi
HOSTUSE:
