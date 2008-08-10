
import builder

class generic_amd64(builder.generic):
	"abstract base class for all amd64 builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"
		self.settings["HOSTUSE"]=["mmx","sse","sse2"]

class arch_amd64(generic_amd64):
	"builder class for generic amd64 (athlon64/opteron)"
	def __init__(self,myspec):
		generic_amd64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -pipe"
		self.settings["CHOST"]="x86_64-pc-linux-gnu"

class arch_core64(arch_amd64):
	def __init__(self,myspec):
		arch_amd64.__init__(self,myspec)
		self.settings["CFLAGS"] ="-march=nocona -O2 -pipe"

def register():
	"Inform main catalyst program of the contents of this plugin."
	return ({"amd64":arch_amd64,"core64":arch_core64}, ("x86_64", ))

