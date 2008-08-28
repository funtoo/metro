? subarch amd64 ~amd64 {
	arch: amd64
	CFLAGS: -O2 -pipe
}

? subarch core64 ~core64 {
	arch: amd64
	CFLAGS: -march=nocona -O2 -pipe
}

? arch amd64 {
	CHOST: x86_64-pc-linux-gnu
}
