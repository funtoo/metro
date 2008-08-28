? subarch x86 ~x86 {
	arch: x86
	cflags: -O2 -mtune=i686 -pipe
	chost: i486-pc-linux-gnu
}

? subarch i686 ~i686 pentium4 ~pentium4 athlon-xp ~athlon-xp {
	arch: x86
	cflags: -O2 -march=$[subarch] -pipe
	chost: i686-pc-linux-gnu
	? subarch pentium4 ~pentium4 {
		hostuse: mmx sse sse2
	}
	? subarch athlon-xp ~athlon-xp {
		hostuse: mmx 3dnow sse
	}
}

? subarch core32 ~core32 {
	arch: x86
	cflags: -march=prescott -O2 -pipe
	chost: i686-pc-linux-gnu
	hostuse: mmx sse sse2
}
