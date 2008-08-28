
"""
Builder class for a stage1 installation tarball build.
"""

from catalyst_support import *
from generic_stage_target import *

class stage1_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=[]
		self.valid_values=["chost"]
		generic_stage_target.__init__(self,spec,addlargs)
	
	def set_stage_path(self):
		self.settings["stage_path"]=normpath(self.settings["chroot_path"]+self.settings["root_path"])
		print "stage1 stage path is "+self.settings["stage_path"]
	
	def set_root_path(self):
		# sets the root path, relative to 'chroot_path', of the stage1 root
		self.settings["root_path"]=normpath("/tmp/stage1root")
		print "stage1 root path is "+self.settings["root_path"]
	
	def set_cleanables(self):
		generic_stage_target.set_cleanables(self)
		self.settings["cleanables"].extend(["/usr/share/gettext",\
		"/usr/lib/python2.2/test", "/usr/lib/python2.2/email",\
		"/usr/lib/python2.2/lib-tk", "/usr/lib/python2.3/test",\
		"/usr/lib/python2.3/email", "/usr/lib/python2.3/lib-tk",\
		"/usr/lib/python2.4/test", "/usr/lib/python2.4/email",\
		"/usr/lib/python2.4/lib-tk", "/usr/share/zoneinfo",\
		"/etc/portage"])

	# XXX: How do these override_foo() functions differ from the ones in generic_stage_target and why aren't they in stage3_target?

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

	def base_dirs(self):
		if os.uname()[0] == "FreeBSD":
			# baselayout no longer creates the .keep files in proc and dev for FreeBSD as it
			# would create them too late...we need them earlier before bind mounting filesystems
			# since proc and dev are not writeable, so...create them here
			if not os.path.exists(self.settings["stage_path"]+"/proc"):
				os.makedirs(self.settings["stage_path"]+"/proc")
			if not os.path.exists(self.settings["stage_path"]+"/dev"):
				os.makedirs(self.settings["stage_path"]+"/dev")
			if not os.path.isfile(self.settings["stage_path"]+"/proc/.keep"):
				try:
					proc_keepfile = open(self.settings["stage_path"]+"/proc/.keep","w") 
					proc_keepfile.write('')
					proc_keepfile.close()
				except IOError:
					print "!!! Failed to create %s" % (self.settings["stage_path"]+"/dev/.keep")
			if not os.path.isfile(self.settings["stage_path"]+"/dev/.keep"):
				try:
					dev_keepfile = open(self.settings["stage_path"]+"/dev/.keep","w")
					dev_keepfile.write('')
					dev_keepfile.close() 
				except IOError:
					print "!!! Failed to create %s" % (self.settings["stage_path"]+"/dev/.keep")
		else:
			pass

	def set_mounts(self):
		# stage_path/proc probably doesn't exist yet, so create it
		if not os.path.exists(self.settings["stage_path"]+"/proc"):
			os.makedirs(self.settings["stage_path"]+"/proc")

		# alter the mount mappings to bind mount proc onto it
		# self.mounts.append("/tmp/stage1root/proc")
		# self.mountmap["/tmp/stage1root/proc"]="/proc"
		# This appears to break baselayout-2.0's makefile, who tries to write to /tmp/stage1root/proc/.keep, so I'm removing it and will see how the build goes

def register(foo):
	foo.update({"stage1":stage1_target})
	return foo
