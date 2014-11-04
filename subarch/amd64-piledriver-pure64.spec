# Support for Trinity APUs and 2nd-gen FX series CPUs.
# See: http://en.wikipedia.org/wiki/Piledriver_(microarchitecture)

[section target]

arch: amd64
arch_desc: pure64

[section portage]

CFLAGS: -march=bdver2 -O2 -pipe
CHOST: x86_64-pc-linux-gnu
HOSTUSE: mmx sse sse2 sse3 sse4 3dnow 3dnowext
