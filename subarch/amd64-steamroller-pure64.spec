# Support for FM2+ Kaveri APU, such as the quad-core AMD A10-7850K APU

[section target]

arch: amd64
arch_desc: pure64

[section portage]

CFLAGS: -march=bdver3 -O2 -pipe
CHOST: x86_64-pc-linux-gnu
HOSTUSE: mmx sse sse2 sse3 sse4 3dnow 3dnowext
