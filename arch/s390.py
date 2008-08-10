
import builder,os
from catalyst_support import *

class generic_s390(builder.generic):
	"abstract base class for all s390 builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"

class generic_s390x(builder.generic):
	"abstract base class for all s390x builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"

class arch_s390(generic_s390):
	"builder class for generic s390"
	def __init__(self,myspec):
		generic_s390.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -pipe"
		self.settings["CHOST"]="s390-ibm-linux-gnu"

class arch_s390x(generic_s390x):
	"builder class for generic s390x"
	def __init__(self,myspec):
		generic_s390x.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -pipe"
		self.settings["CHOST"]="s390x-ibm-linux-gnu"

def register():
	"Inform main catalyst program of the contents of this plugin."
	return ({"s390":arch_s390,"s390x":arch_s390x}, ("s390", "s390x"))
