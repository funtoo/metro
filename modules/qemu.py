#!/usr/bin/python3

qemu_arch_settings = {
	'riscv-64bit': {
		'qemu_binary': 'qemu-riscv64',
		'qemu_cpu': 'sifive-u54',
		'hexstring': [ '7f454c460201010000000000000000000200f3', '7f454c460201010000000000000000000300f3' ]
	},
	'arm-64bit': {
		'qemu_binary': 'qemu-aarch64',
		'qemu_cpu': 'cortex-a53',
		'hexstring': '7f454c460201010000000000000000000200b7',
	},
	'arm-32bit': {
		'qemu_binary': 'qemu-arm',
		'qemu_cpu': 'cortex-a7',
		'hexstring': '7f454c46010101000000000000000000020028',
	}
}

native_support = {
	'riscv': [],
	'x86-64bit': ['x86-32bit'],
	'x86-32bit': [],
	'arm-64bit': ['arm-32bit'],
	'arm-32bit': []
}
