
"""
Builder class for a LiveCD stage2 build.
"""

import os,string,types,stat,shutil
from catalyst_support import *
from generic_stage_target import *

class livecd_stage2_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=["boot/kernel"]
		
		self.valid_values=[]
		
		self.valid_values.extend(self.required_values)
		self.valid_values.extend(["livecd/cdtar","livecd/empty","livecd/rm",\
			"livecd/unmerge","livecd/iso","livecd/gk_mainargs","livecd/type",\
			"livecd/readme","livecd/motd","livecd/overlay",\
			"livecd/modblacklist","livecd/splash_theme","livecd/splash_type",\
			"livecd/rcadd","livecd/rcdel","livecd/fsscript","livecd/xinitrc",\
			"livecd/root_overlay","livecd/devmanager","livecd/users",\
			"portage_overlay","livecd/cdfstype","livecd/fstype","livecd/fsops",\
			"livecd/linuxrc","livecd/bootargs","gamecd/conf","livecd/xdm",\
			"livecd/xsession","livecd/volid"])
		
		generic_stage_target.__init__(self,spec,addlargs)
		if not self.settings.has_key("livecd/type"):
			self.settings["livecd/type"] = "generic-livecd"

		file_locate(self.settings, ["cdtar","controller_file"])
	
	def set_source_path(self):
		self.settings["source_path"]=normpath(self.settings["storedir"]+"/builds/"+self.settings["source_subpath"]+".tar.bz2")
		if os.path.isfile(self.settings["source_path"]):
			self.settings["source_path_hash"]=generate_hash(self.settings["source_path"])
		else:
			self.settings["source_path"]=normpath(self.settings["storedir"]+"/tmp/"+self.settings["source_subpath"]+"/")
		if not os.path.exists(self.settings["source_path"]):
			raise CatalystError,"Source Path: "+self.settings["source_path"]+" does not exist."
	
	def set_spec_prefix(self):
	    self.settings["spec_prefix"]="livecd"

	def set_target_path(self):
		self.settings["target_path"]=normpath(self.settings["storedir"]+"/builds/"+self.settings["target_subpath"]+"/")
		if True:	
			# first clean up any existing target stuff
			if os.path.isdir(self.settings["target_path"]):
				cmd("rm -rf "+self.settings["target_path"],
				"Could not remove existing directory: "+self.settings["target_path"],env=self.env)
			if not os.path.exists(self.settings["target_path"]):
				os.makedirs(self.settings["target_path"])

	def run_local(self):
		# what modules do we want to blacklist?
		if self.settings.has_key("livecd/modblacklist"):
			try:
				myf=open(self.settings["chroot_path"]+"/etc/hotplug/blacklist","a")
			except:
				self.unbind()
				raise CatalystError,"Couldn't open "+self.settings["chroot_path"]+"/etc/hotplug/blacklist."
			
			myf.write("\n#Added by Catalyst:")
			for x in self.settings["livecd/modblacklist"]:
				myf.write("\n"+x)
			myf.close()
	
	def unpack(self):
		unpack=True
		display_msg=None

		if os.path.isdir(self.settings["source_path"]):
			unpack_cmd="rsync -a --delete "+self.settings["source_path"]+" "+self.settings["chroot_path"]
			display_msg="\nStarting rsync from "+self.settings["source_path"]+"\nto "+\
				self.settings["chroot_path"]+" (This may take some time) ...\n"
			error_msg="Rsync of "+self.settings["source_path"]+" to "+self.settings["chroot_path"]+" failed."

		if unpack:
			self.mount_safety_check()

			if not os.path.exists(self.settings["chroot_path"]):
				os.makedirs(self.settings["chroot_path"])

			if not os.path.exists(self.settings["chroot_path"]+"/tmp"):
				os.makedirs(self.settings["chroot_path"]+"/tmp",1777)

			if self.settings.has_key("PKGCACHE"):
				if not os.path.exists(self.settings["pkgcache_path"]):
					os.makedirs(self.settings["pkgcache_path"],0755)

			if not display_msg:
				raise CatalystError,"Could not find appropriate source. Please check the 'source_subpath' setting in the spec file."

			print display_msg
			cmd(unpack_cmd,error_msg,env=self.env)


	def set_action_sequence(self):
		self.settings["action_sequence"]=["unpack","unpack_snapshot",\
				"config_profile_link","setup_confdir","portage_overlay",\
				"bind","chroot_setup","setup_environment","run_local",\
				"build_kernel"]
		if not self.settings.has_key("FETCH"):
			self.settings["action_sequence"] += ["bootloader","preclean",\
				"livecd_update","root_overlay","fsscript","rcupdate","unmerge",\
				"unbind","remove","empty","target_setup",\
				"setup_overlay","create_iso"]

def register(foo):
	foo.update({"livecd-stage2":livecd_stage2_target})
	return foo
