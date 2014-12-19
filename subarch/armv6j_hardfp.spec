[section target]

arch: arm
arch_desc: arm-32bit

[section portage]

CFLAGS: -O2 -pipe -march=armv6j -mfpu=vfp -mfloat-abi=hard
CHOST: armv6j-hardfloat-linux-gnueabi
CHOST_OVERRIDE: $[:CHOST]
HOSTUSE:
