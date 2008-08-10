
import builder,os
from catalyst_support import *

class generic_x86(builder.generic):
	"abstract base class for all x86 builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		if self.settings["buildarch"]=="amd64":
			if not os.path.exists("/bin/linux32") and not os.path.exists("/usr/bin/linux32"):
					raise CatalystError,"required executable linux32 not found (\"emerge setarch\" to fix.)"
			self.settings["CHROOT"]="linux32 chroot"
			self.settings["crosscompile"] = False;
		else:
			self.settings["CHROOT"]="chroot"

class arch_x86(generic_x86):
	"builder class for generic x86 (386+)"
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mtune=i686 -pipe"
		self.settings["CHOST"]="i386-pc-linux-gnu"

class arch_i386(generic_x86):
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=i386 -pipe"
		self.settings["CHOST"]="i386-pc-linux-gnu"

class arch_i486(generic_x86):
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=i486 -pipe"
		self.settings["CHOST"]="i486-pc-linux-gnu"

class arch_i586(generic_x86):
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=i586 -pipe"
		self.settings["CHOST"]="i586-pc-linux-gnu"

class arch_pentium_mmx(arch_i586):
	def __init__(self,myspec):
		arch_i586.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=pentium-mmx -pipe"
		self.settings["HOSTUSE"]=["mmx"]
	
class arch_i686(generic_x86):
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=i686 -pipe"
		self.settings["CHOST"]="i686-pc-linux-gnu"

class arch_athlon(generic_x86):
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=athlon -pipe"
		self.settings["CHOST"]="i686-pc-linux-gnu"
		self.settings["HOSTUSE"]=["mmx","3dnow"]

class arch_athlon_xp(generic_x86):
	#this handles XP and MP processors
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=athlon-xp -pipe"
		self.settings["CHOST"]="i686-pc-linux-gnu"
		self.settings["HOSTUSE"]=["mmx","3dnow","sse"]

class arch_pentium4(generic_x86):
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=pentium4 -pipe"
		self.settings["CHOST"]="i686-pc-linux-gnu"
		self.settings["HOSTUSE"]=["mmx","sse","sse2"]

class arch_pentium3(generic_x86):
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=pentium3 -pipe"
		self.settings["CHOST"]="i686-pc-linux-gnu"
		self.settings["HOSTUSE"]=["mmx","sse"]

class arch_core32(generic_x86):
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-march=prescott -O2 -pipe"
		self.settings["CHOST"]="i686-pc-linux-gnu"
		self.settings["HOSTUSE"]=["mmx","sse","sse2"]

def register():
	"Inform main catalyst program of the contents of this plugin."
	return ({"pentium4":arch_pentium4,"x86":arch_x86,"i386":arch_i386,"i486":arch_i486,"i586":arch_i586,"i686":arch_i686,"athlon":arch_athlon,
	"core32":arch_core32,"athlon-xp":arch_athlon_xp,"athlon-mp":arch_athlon_xp,"pentium3":arch_pentium3,"pentium-mmx":arch_pentium_mmx},
	('i386', 'i486', 'i586', 'i686'))

