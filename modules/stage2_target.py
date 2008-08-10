
"""
Builder class for a stage2 installation tarball build.
"""

from catalyst_support import *
from generic_stage_target import *

class stage2_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=[]
		self.valid_values=["chost"]
		generic_stage_target.__init__(self,spec,addlargs)
		
	def set_source_path(self):
		if self.settings.has_key("SEEDCACHE") and os.path.isdir(normpath(self.settings["storedir"]+"/tmp/"+self.settings["source_subpath"]+"/tmp/stage1root/")):
			self.settings["source_path"]=normpath(self.settings["storedir"]+"/tmp/"+self.settings["source_subpath"]+"/tmp/stage1root/")
		else:
			self.settings["source_path"]=normpath(self.settings["storedir"]+"/builds/"+self.settings["source_subpath"]+".tar.bz2")
			if os.path.isfile(self.settings["source_path"]):
				if os.path.exists(self.settings["source_path"]):
				# XXX: Is this even necessary if the previous check passes?
					self.settings["source_path_hash"]=generate_hash(self.settings["source_path"],\
						hash_function=self.settings["hash_function"],verbose=False)
		print "Source path set to "+self.settings["source_path"]
		if os.path.isdir(self.settings["source_path"]):
			print "\tIf this is not desired, remove this directory or turn of seedcache in the options of catalyst.conf"
			print "\tthe source path will then be "+normpath(self.settings["storedir"]+"/builds/"+self.settings["source_subpath"]+".tar.bz2\n")

	# XXX: How do these override_foo() functions differ from the ones in
	# generic_stage_target and why aren't they in stage3_target?

	def set_cleanables(self):
		generic_stage_target.set_cleanables(self)
		self.settings["cleanables"].extend(["/etc/portage"])
	
	def override_chost(self):
		if self.settings.has_key("chost"):
			self.settings["CHOST"]=list_to_string(self.settings["chost"])

	def override_cflags(self):
		if self.settings.has_key("cflags"):
			self.settings["CFLAGS"]=list_to_string(self.settings["cflags"])

	def override_cxxflags(self):
		if self.settings.has_key("cxxflags"):
			self.settings["CXXFLAGS"]=list_to_string(self.settings["cxxflags"])

	def override_ldflags(self):
		if self.settings.has_key("ldflags"):
			self.settings["LDFLAGS"]=list_to_string(self.settings["ldflags"])

	def set_portage_overlay(self):
			generic_stage_target.set_portage_overlay(self)
			if self.settings.has_key("portage_overlay"):
				print "\nWARNING !!!!!"
				print "\tUsing an portage overlay for earlier stages could cause build issues."
				print "\tIf you break it, you buy it. Don't complain to us about it."
				print "\tDont say we did not warn you\n"

def register(foo):
	foo.update({"stage2":stage2_target})
	return foo
