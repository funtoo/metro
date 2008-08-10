
import os,builder
from catalyst_support import *

# gcc-3.3.3 is required to do G5 optimizations
# install a 32bit kernel personality changer (that works) before building on a
# ppc64 host new gcc optimization feature requires -fno-strict-aliasing needed,
# otherwise code complains use the experimental thing for nptl builds

class generic_ppc(builder.generic):
	"abstract base class for all ppc builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["CHOST"]="powerpc-unknown-linux-gnu"
		if self.settings["buildarch"]=="ppc64":
			if not os.path.exists("/bin/linux32") and not os.path.exists("/usr/bin/linux32"):
				raise CatalystError,"required executable linux32 not found (\"emerge setarch\" to fix.)"
			self.settings["CHROOT"]="linux32 chroot"
			self.settings["crosscompile"] = False;
		else:
			self.settings["CHROOT"]="chroot"

class arch_power_ppc(generic_ppc):
	"builder class for generic powerpc/power"
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mcpu=common -mtune=common -fno-strict-aliasing -pipe"

class arch_ppc(generic_ppc):
	"builder class for generic powerpc"
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mcpu=powerpc -mtune=powerpc -fno-strict-aliasing -pipe"

class arch_power(generic_ppc):
	"builder class for generic power"
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mcpu=power -mtune=power -fno-strict-aliasing -pipe"

class arch_g3(generic_ppc):
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mcpu=G3 -mtune=G3 -fno-strict-aliasing -pipe"

class arch_g4(generic_ppc):
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mcpu=G4 -mtune=G4 -maltivec -mabi=altivec -fno-strict-aliasing -pipe"
		self.settings["HOSTUSE"]=["altivec"]

class arch_g5(generic_ppc):
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mcpu=G5 -mtune=G5 -maltivec -mabi=altivec -fno-strict-aliasing -pipe"
		self.settings["HOSTUSE"]=["altivec"]

def register():
	"Inform main catalyst program of the contents of this plugin."
	return ({"ppc":arch_ppc,"power":arch_power,"power-ppc":arch_power_ppc,"g3":arch_g3,"g4":arch_g4,"g5":arch_g5}, 
	("ppc","powerpc"))

