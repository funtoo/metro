
import builder,os
from catalyst_support import *

class generic_mips(builder.generic):
	"Abstract base class for all mips builders [Big-endian]"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"
		self.settings["CHOST"]="mips-unknown-linux-gnu"

class generic_mipsel(builder.generic):
	"Abstract base class for all mipsel builders [Little-endian]"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"
		self.settings["CHOST"]="mipsel-unknown-linux-gnu"

class arch_mips1(generic_mips):
	"Builder class for MIPS I [Big-endian]"
	def __init__(self,myspec):
		generic_mips.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips1 -mabi=32 -pipe"

class arch_mips2(generic_mips):
	"Builder class for MIPS II [Big-endian]"
	def __init__(self,myspec):
		generic_mips.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips2 -mabi=32 -pipe"

class arch_mips3(generic_mips):
	"Builder class for MIPS III [Big-endian]"
	def __init__(self,myspec):
		generic_mips.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips3 -mabi=32 -pipe"

class arch_mips4(generic_mips):
	"Builder class for MIPS IV [Big-endian]"
	def __init__(self,myspec):
		generic_mips.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips4 -mabi=32 -pipe"

class arch_mips4n32(generic_mips):
	"Builder class for MIPS IV [Big-endian N32]"
	def __init__(self,myspec):
		generic_mips.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips4 -mabi=n32 -pipe"
		self.settings["CHOST"]="mips64-unknown-linux-gnu"

class arch_mipsel1(generic_mipsel):
	"Builder class for all MIPS I [Little-endian]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips1 -mabi=32 -pipe"

class arch_mipsel2(generic_mipsel):
	"Builder class for all MIPS II [Little-endian]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips2 -mabi=32 -pipe"

class arch_mipsel3(generic_mipsel):
	"Builder class for all MIPS III [Little-endian]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips3 -mabi=32 -pipe"

class arch_mipsel3n32(generic_mipsel):
	"Builder class for all MIPS III [Little-endian N32]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips3 -mabi=n32 -pipe"
		self.settings["CHOST"]="mips64el-unknown-linux-gnu"

class arch_mipsel4(generic_mipsel):
	"Builder class for all MIPS IV [Little-endian]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips4 -mabi=32 -pipe"

class arch_mipsel4n32(generic_mipsel):
	"Builder class for all MIPS IV [Little-endian N32]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips4 -mabi=n32 -pipe"
		self.settings["CHOST"]="mips64el-unknown-linux-gnu"



def register():
	"Inform main catalyst program of the contents of this plugin."
	return ({ 
			"mips"		:arch_mips1,
			"mips1"		:arch_mips1,
			"mips2"		:arch_mips2,
			"mips3"		:arch_mips3,
			"mips4"		:arch_mips4,
			"mips4n32"	:arch_mips4n32,
			"mipsel"	:arch_mipsel1,
			"mipsel1"	:arch_mipsel1,
			"mipsel2"	:arch_mipsel2,
			"mipsel3"	:arch_mipsel3,
			"mipsel3n32"	:arch_mipsel3n32,
			"mipsel4"	:arch_mipsel4,
			"mipsel4n32"	:arch_mipsel4n32,
			"sgir4k"	:arch_mips3, 
			"sgir5k"	:arch_mips4,
			"sgir10kplus"	:arch_mips4,
			"loongson"	:arch_mipsel3,
			"cobalt"	:arch_mipsel4
	}, ("mips","mips64"))
