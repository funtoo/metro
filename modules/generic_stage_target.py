
"""
This class does all of the chroot setup, copying of files, etc. It is
the driver class for pretty much everything that Catalyst does.
"""

import os,string,imp,types,shutil
from catalyst_support import *
from generic_target import *
from stat import *
import catalyst_lock
class generic_stage_target(generic_target):

	def __init__(self,myspec,addlargs):
		self.required_values.extend(["version_stamp","target","subarch",\
			"rel_type","profile","snapshot","source_subpath"])
		
		self.valid_values.extend(["version_stamp","target","subarch","keywords",\
			"rel_type","profile","snapshot","source_subpath","portage_confdir",\
			"cflags","cxxflags","ldflags","cbuild","hostuse","portage_overlay",\
			"distcc_hosts","makeopts","pkgcache_path","kerncache_path","portdir","portname"])
		
		self.set_valid_build_kernel_vars(addlargs)
		generic_target.__init__(self,myspec,addlargs)

		# The semantics of subarchmap and machinemap changed a bit in 2.0.3 to
		# work better with vapier's CBUILD stuff. I've removed the "monolithic"
		# machinemap from this file and split up its contents amongst the various
		# arch/foo.py files.
		#
		# When register() is called on each module in the arch/ dir, it now
		# returns a tuple instead of acting on the subarchmap dict that is
		# passed to it. The tuple contains the values that were previously
		# added to subarchmap as well as a new list of CHOSTs that go along
		# with that arch. This allows us to build machinemap on the fly based
		# on the keys in subarchmap and the values of the 2nd list returned
		# (tmpmachinemap).
		#
		# Also, after talking with vapier. I have a slightly better idea of what
		# certain variables are used for and what they should be set to. Neither
		# 'buildarch' or 'hostarch' are used directly, so their value doesn't
		# really matter. They are just compared to determine if we are
		# cross-compiling. Because of this, they are just set to the name of the
		# module in arch/ that the subarch is part of to make things simpler.
		# The entire build process is still based off of 'subarch' like it was
		# previously. -agaffney

		self.archmap = {}
		self.subarchmap = {}
		machinemap = {}
		for x in [x[:-3] for x in os.listdir(self.settings["sharedir"]+"/arch/") if x.endswith(".py")]:
			try:
				fh=open(self.settings["sharedir"]+"/arch/"+x+".py")
				# This next line loads the plugin as a module and assigns it to
				# archmap[x]
				self.archmap[x]=imp.load_module(x,fh,"arch/"+x+".py",(".py","r",imp.PY_SOURCE))
				# This next line registers all the subarches supported in the
				# plugin
				tmpsubarchmap, tmpmachinemap = self.archmap[x].register()
				self.subarchmap.update(tmpsubarchmap)
				for machine in tmpmachinemap:
					machinemap[machine] = x
				for subarch in tmpsubarchmap:
					machinemap[subarch] = x
				fh.close()	
			except IOError:
				# This message should probably change a bit, since everything in the dir should
				# load just fine. If it doesn't, it's probably a syntax error in the module
				msg("Can't find "+x+".py plugin in "+self.settings["sharedir"]+"/arch/")

		# If subarch is specified as "~pentium4", set the realsubarch to "pentium4". This info will be
		# used when validating the subarch so a user-specified "~pentium4" will be interpreted as valid.

		# We also use an initial "~" as a trigger to build an unstable version of the portage tree. This
		# means we need to use ~arch rather than arch in ACCEPT_KEYWORDS. So if someone specified "~pentium4"
		# as subarch, we would set treearch to "~x86" and later write this into make.conf.
		
		# hostarch is based off of the subarch in the spec file - if "~pentium4" is specified, first we look
		# at the "pentium4" (realsubarch) part. Then we find the arch that has defined this subarch in its
		# arch/<arch>.py class definition file. That becomes our hostarch setting:
		
		if self.settings["subarch"][0] == "~":
			self.settings["realsubarch"] = self.settings["subarch"][1:]
			self.settings["hostarch"] = machinemap[self.settings["realsubarch"]]
			self.settings["treearch"] = "~"+self.settings["hostarch"]
		else:
			self.settings["realsubarch"] = self.settings["subarch"]
			self.settings["hostarch"] = machinemap[self.settings["realsubarch"]]
			self.settings["treearch"] = self.settings["hostarch"]
		
		print "DEBUG: realsubarch: ",self.settings["realsubarch"]
		print "DEBUG: treearch: ",self.settings["treearch"]
		
		try:
			self.settings["buildarch"] = machinemap[os.uname()[4]]
		except KeyError:
			raise CatalystError, "Unknown build machine type "+os.uname()[4]

		print "DEBUG: buildarch: ", self.settings["buildarch"]
		print "DEBUG: hostarch: ",self.settings["hostarch"]	

		self.settings["crosscompile"] = (self.settings["hostarch"] != self.settings["buildarch"])

		# Call arch constructor, pass our settings
		try:
			# look up based on realsubarch....
			self.arch=self.subarchmap[self.settings["realsubarch"]](self.settings)
		except KeyError:
			# display error using user-specified subarch...
			print "Invalid subarch: "+self.settings["subarch"]
			print "Choose one of the following:",
			for x in self.subarchmap:
				print x,
				# list unstable versions as well:
				print "~"+x,
			print
			sys.exit(2)

		# All the ~x86, ~pentium4, etc. unstable subarch build logic should be done now. Now we need to make
		# sure that we use the new variables for paths, below...

		print "Using target:",self.settings["target"]
		# print a nice informational message:
		if self.settings["buildarch"]==self.settings["hostarch"]:
			print "Building natively for",self.settings["hostarch"]
		elif self.settings["crosscompile"]:
			print "Cross-compiling on",self.settings["buildarch"],"for different machine type",\
				self.settings["hostarch"]
		else:
			print "Building on",self.settings["buildarch"],"for alternate personality type",\
				self.settings["hostarch"]

		# This should be first to be set as other set_ options depend on this
		self.set_spec_prefix()
		
		# define all of our core variables
		self.set_target_profile()
		self.set_target_subpath()
		self.set_source_subpath()

		# set paths
		self.set_snapshot_path()
		self.set_root_path()
		self.set_source_path()
		self.set_snapcache_path()
		self.set_chroot_path()
		self.set_dest_path()
		self.set_stage_path()
		self.set_target_path()
		
		self.set_controller_file()
		self.set_action_sequence()
		self.set_use()
		self.set_cleanables()
		self.set_iso_volume_id()
		self.set_build_kernel_vars()
		self.set_fsscript()
		self.set_archscript()
		self.set_runscript()
		self.set_install_mask()
		self.set_rcadd()
		self.set_rcdel()
		self.set_cdtar()
		self.set_fstype()
		self.set_fsops()
		self.set_iso()
		self.set_packages()
		self.set_rm()
		self.set_linuxrc()
		self.set_overlay()	
		self.set_portage_overlay()	
		self.set_root_overlay()	
		
		# This next line checks to make sure that the specified variables exist
		# on disk.
		#pdb.set_trace()
		file_locate(self.settings,["source_path","snapshot_path","distdir"],expand=0)
		# If we are using portage_confdir, check that as well.
		if self.settings.has_key("portage_confdir"):
			file_locate(self.settings,["portage_confdir"],expand=0)
		
		# setup our mount points
		if self.settings.has_key("SNAPCACHE"):
			self.mounts=[ "/proc","/dev","/usr/portage","/usr/portage/distfiles" ]
			self.mountmap={"/proc":"/proc", "/dev":"/dev", "/dev/pts":"/dev/pts",\
				"/usr/portage":self.settings["snapshot_cache_path"]+"/portage",\
				"/usr/portage/distfiles":self.settings["distdir"]}
		else:
			self.mounts=[ "/proc","/dev","/usr/portage/distfiles" ]
			self.mountmap={"/proc":"/proc", "/dev":"/dev", "/dev/pts":"/dev/pts",\
				"/usr/portage/distfiles":self.settings["distdir"]}
		if os.uname()[0] == "Linux":
			self.mounts.append("/dev/pts")

		self.set_mounts()

		# Configure any user specified options (either in catalyst.conf or on
		# the command line).
		if self.settings.has_key("PKGCACHE"):
			self.set_pkgcache_path()
			print "Location of the package cache is " + self.settings["pkgcache_path"]
			self.mounts.append("/usr/portage/packages")
			self.mountmap["/usr/portage/packages"]=self.settings["pkgcache_path"]
		
		if self.settings.has_key("KERNCACHE"):
			self.set_kerncache_path()
			print "Location of the kerncache is " + self.settings["kerncache_path"]
			self.mounts.append("/tmp/kerncache")
			self.mountmap["/tmp/kerncache"]=self.settings["kerncache_path"]

		if self.settings.has_key("CCACHE"):
			if os.environ.has_key("CCACHE_DIR"):
				ccdir=os.environ["CCACHE_DIR"]
				del os.environ["CCACHE_DIR"]
			else:
				ccdir="/root/.ccache"
			if not os.path.isdir(ccdir):
					raise CatalystError,\
						"Compiler cache support can't be enabled (can't find "+ccdir+")"
			self.mounts.append("/var/tmp/ccache")
			self.mountmap["/var/tmp/ccache"]=ccdir
			# for the chroot:
			self.env["CCACHE_DIR"]="/var/tmp/ccache"	

		if self.settings.has_key("ICECREAM"):
			self.mounts.append("/var/cache/icecream")
			self.mountmap["/var/cache/icecream"]="/var/cache/icecream"
			self.env["PATH"]="/usr/lib/icecc/bin:"+self.env["PATH"]

	def override_cbuild(self):
		if self.makeconf.has_key("CBUILD"):
			self.settings["CBUILD"]=self.makeconf["CBUILD"]

	def override_chost(self):
		if self.makeconf.has_key("CHOST"):
			self.settings["CHOST"]=self.makeconf["CHOST"]
	
	def override_cflags(self):
		if self.makeconf.has_key("CFLAGS"):
			self.settings["CFLAGS"]=self.makeconf["CFLAGS"]

	def override_cxxflags(self):	
		if self.makeconf.has_key("CXXFLAGS"):
			self.settings["CXXFLAGS"]=self.makeconf["CXXFLAGS"]
	
	def override_ldflags(self):
		if self.makeconf.has_key("LDFLAGS"):
			self.settings["LDFLAGS"]=self.makeconf["LDFLAGS"]
	
	def set_install_mask(self):
		if self.settings.has_key("install_mask"):
			if type(self.settings["install_mask"]) != types.StringType:
				self.settings["install_mask"]=string.join(self.settings["install_mask"])
	
	def set_spec_prefix(self):
		self.settings["spec_prefix"]=self.settings["target"]

	def set_target_profile(self):
		self.settings["target_profile"]=self.settings["profile"]
	
	def set_target_subpath(self):
		self.settings["target_subpath"]=self.settings["rel_type"]+"/"+self.settings["target"]+\
			"-"+self.settings["subarch"]+"-"+self.settings["version_stamp"]
	
	def set_source_subpath(self):
		if type(self.settings["source_subpath"]) != types.StringType:
			raise CatalystError, "source_subpath should have been a string. Perhaps you have something wrong in your spec file?"
	
	def set_pkgcache_path(self):
		if self.settings.has_key("pkgcache_path"):
			if type(self.settings["pkgcache_path"]) != types.StringType:
				self.settings["pkgcache_path"]=normpath(string.join(self.settings["pkgcache_path"]))
		else:
			self.settings["pkgcache_path"]=normpath(self.settings["storedir"]+"/packages/"+\
				self.settings["target_subpath"]+"/")

	def set_kerncache_path(self):
		if self.settings.has_key("kerncache_path"):
			if type(self.settings["kerncache_path"]) != types.StringType:
				self.settings["kerncache_path"]=normpath(string.join(self.settings["kerncache_path"]))
		else:
			self.settings["kerncache_path"]=normpath(self.settings["storedir"]+"/kerncache/"+\
				self.settings["target_subpath"]+"/")

	def set_target_path(self):
		self.settings["target_path"]=normpath(self.settings["storedir"]+"/builds/"+\
			self.settings["target_subpath"]+".tar.bz2")
		if True:
			# first clean up any existing target stuff
			if os.path.isfile(self.settings["target_path"]):
				cmd("rm -f "+self.settings["target_path"], \
				"Could not remove existing file: "+self.settings["target_path"],env=self.env)
		
			if not os.path.exists(self.settings["storedir"]+"/builds/"):
				os.makedirs(self.settings["storedir"]+"/builds/")

	def set_archscript(self):
	    if self.settings.has_key(self.settings["spec_prefix"]+"/archscript"):
		print "\nWarning!!!  "
		print "\t"+self.settings["spec_prefix"]+"/archscript" + " is deprecated and no longer used.\n"
	def set_runscript(self):
	    if self.settings.has_key(self.settings["spec_prefix"]+"/runscript"):
		print "\nWarning!!!  "
		print "\t"+self.settings["spec_prefix"]+"/runscript" + " is deprecated and no longer used.\n"

	def set_fsscript(self):	
		if self.settings.has_key(self.settings["spec_prefix"]+"/fsscript"):
			self.settings["fsscript"]=self.settings[self.settings["spec_prefix"]+"/fsscript"]
			del self.settings[self.settings["spec_prefix"]+"/fsscript"]
	
	def set_rcadd(self):	
		if self.settings.has_key(self.settings["spec_prefix"]+"/rcadd"):
			self.settings["rcadd"]=self.settings[self.settings["spec_prefix"]+"/rcadd"]
			del self.settings[self.settings["spec_prefix"]+"/rcadd"]
	
	def set_rcdel(self):	
		if self.settings.has_key(self.settings["spec_prefix"]+"/rcdel"):
			self.settings["rcdel"]=self.settings[self.settings["spec_prefix"]+"/rcdel"]
			del self.settings[self.settings["spec_prefix"]+"/rcdel"]

	def set_cdtar(self):	
		if self.settings.has_key(self.settings["spec_prefix"]+"/cdtar"):
			self.settings["cdtar"]=normpath(self.settings[self.settings["spec_prefix"]+"/cdtar"])
			del self.settings[self.settings["spec_prefix"]+"/cdtar"]
	
	def set_iso(self):	
		if self.settings.has_key(self.settings["spec_prefix"]+"/iso"):
			self.settings["iso"]=normpath(self.settings[self.settings["spec_prefix"]+"/iso"])
			del self.settings[self.settings["spec_prefix"]+"/iso"]

	def set_fstype(self):	
		if self.settings.has_key(self.settings["spec_prefix"]+"/cdfstype"):
			print "\nWarning!!!  "
			print self.settings["spec_prefix"]+"/cdfstype" + " is deprecated and may be removed."
			print "\tUse "+self.settings["spec_prefix"]+"/fstype" + " instead."
			print "\tConverting to "+self.settings["spec_prefix"]+"/fstype" + " internally."
			print "\tContinuing ....\n"
			self.settings["fstype"]=self.settings[self.settings["spec_prefix"]+"/cdfstype"]
			del self.settings[self.settings["spec_prefix"]+"/cdfstype"]
		
		if self.settings.has_key(self.settings["spec_prefix"]+"/fstype"):
			self.settings["fstype"]=self.settings[self.settings["spec_prefix"]+"/fstype"]
			del self.settings[self.settings["spec_prefix"]+"/fstype"]

		if not self.settings.has_key("fstype"):
			self.settings["fstype"]="normal"
			for x in self.valid_values:
				if x ==  self.settings["spec_prefix"]+"/fstype" or x == self.settings["spec_prefix"]+"/cdfstype":
					print "\n"+self.settings["spec_prefix"]+"/fstype is being set to the default of \"normal\"\n"

	def set_fsops(self):
		if self.settings.has_key("fstype"):
			self.valid_values.append("fsops")
			if self.settings.has_key(self.settings["spec_prefix"]+"/fsops"):
				self.settings["fsops"]=self.settings[self.settings["spec_prefix"]+"/fsops"]
				del self.settings[self.settings["spec_prefix"]+"/fsops"]
	
	def set_source_path(self):
		self.settings["source_path"]=normpath(self.settings["storedir"]+"/builds/"+self.settings["source_subpath"]+".tar.bz2")
		print "Source path set to "+self.settings["source_path"]

	def set_dest_path(self):
		if self.settings.has_key("root_path"):
			self.settings["destpath"]=normpath(self.settings["chroot_path"]+self.settings["root_path"])
		else:
			self.settings["destpath"]=normpath(self.settings["chroot_path"])

	def set_cleanables(self):
		self.settings["cleanables"]=["/etc/resolv.conf","/var/tmp/*","/tmp/*","/root/*",\
						"/usr/portage"]

	def set_snapshot_path(self):
		self.settings["snapshot_path"]=normpath(self.settings["storedir"]+"/snapshots/"+self.settings["portname"]+"-"+self.settings["snapshot"]+".tar.bz2")
		
	def set_snapcache_path(self):
		if self.settings.has_key("SNAPCACHE"):
			self.settings["snapshot_cache_path"]=normpath(self.settings["snapshot_cache"]+"/"+self.settings["snapshot"]+"/")
			self.snapcache_lock=catalyst_lock.LockDir(self.settings["snapshot_cache_path"])
			print "Caching snapshot to " + self.settings["snapshot_cache_path"]
	
	def set_chroot_path(self):
		# Note the trailing slash is very important and things would break without it
		self.settings["chroot_path"]=normpath(self.settings["storedir"]+"/tmp/"+self.settings["target_subpath"]+"/")
		self.chroot_lock=catalyst_lock.LockDir(self.settings["chroot_path"])
	
	def set_controller_file(self):
		self.settings["controller_file"]=normpath(self.settings["sharedir"]+"/targets/"+self.settings["target"]+"/"+self.settings["target"]+"-controller.sh")

	def set_iso_volume_id(self):
                if self.settings.has_key(self.settings["spec_prefix"]+"/volid"):
			self.settings["iso_volume_id"] = self.settings[self.settings["spec_prefix"]+"/volid"]
			if len(self.settings["iso_volume_id"])>32:
				raise CatalystError,"ISO VOLUME ID: volid must not exceed 32 characters."
		else:
			self.settings["iso_volume_id"] = "catalyst " + self.settings["snapshot"] 
															
	def set_action_sequence(self):
		# Default action sequence for run method
		self.settings["action_sequence"]=["unpack","unpack_snapshot",\
				"config_profile_link","setup_confdir","portage_overlay",\
				"base_dirs","bind","chroot_setup","setup_environment",\
				"run_local","preclean","unbind","clean"]
#		if self.settings.has_key("TARBALL") or \
#			not self.settings.has_key("FETCH"):
		if not self.settings.has_key("FETCH"):
			self.settings["action_sequence"].append("capture")
	
	def set_use(self):
		if self.settings.has_key(self.settings["spec_prefix"]+"/use"):
			self.settings["use"]=self.settings[self.settings["spec_prefix"]+"/use"]
			del self.settings[self.settings["spec_prefix"]+"/use"]
		if self.settings.has_key("use"):
		    if type(self.settings["use"])==types.StringType:
			self.settings["use"]=self.settings["use"].split()

	def set_stage_path(self):
			self.settings["stage_path"]=normpath(self.settings["chroot_path"])
	
	def set_mounts(self):
		pass

	def set_packages(self):
		pass

	def set_rm(self):
	    if self.settings.has_key(self.settings["spec_prefix"]+"/rm"):
		if type(self.settings[self.settings["spec_prefix"]+"/rm"])==types.StringType:
		    self.settings[self.settings["spec_prefix"]+"/rm"]=self.settings[self.settings["spec_prefix"]+"/rm"].split()

	def set_linuxrc(self):
	    if self.settings.has_key(self.settings["spec_prefix"]+"/linuxrc"):
			if type(self.settings[self.settings["spec_prefix"]+"/linuxrc"])==types.StringType:
				self.settings["linuxrc"]=self.settings[self.settings["spec_prefix"]+"/linuxrc"]
				del self.settings[self.settings["spec_prefix"]+"/linuxrc"]

	def set_portage_overlay(self):
		if self.settings.has_key("portage_overlay"):
			if type(self.settings["portage_overlay"])==types.StringType:
				self.settings["portage_overlay"]=self.settings["portage_overlay"].split()
			print "portage_overlay directories are set to: \"" + string.join(self.settings["portage_overlay"])+"\""
	
	def set_overlay(self):
		if self.settings.has_key(self.settings["spec_prefix"]+"/overlay"):
			if type(self.settings[self.settings["spec_prefix"]+"/overlay"])==types.StringType:
				self.settings[self.settings["spec_prefix"]+"/overlay"]=self.settings[self.settings["spec_prefix"]+"/overlay"].split()
	
	def set_root_overlay(self):
		if self.settings.has_key(self.settings["spec_prefix"]+"/root_overlay"):
			if type(self.settings[self.settings["spec_prefix"]+"/root_overlay"])==types.StringType:
				self.settings[self.settings["spec_prefix"]+"/root_overlay"]=self.settings[self.settings["spec_prefix"]+"/root_overlay"].split()
	

	def set_root_path(self):
		# ROOT= variable for emerges
		self.settings["root_path"]="/"

	def set_valid_build_kernel_vars(self,addlargs):
		if addlargs.has_key("boot/kernel"):
			if type(addlargs["boot/kernel"]) == types.StringType:
				loopy=[addlargs["boot/kernel"]]
			else:
				loopy=addlargs["boot/kernel"]
			    
			for x in loopy:
				self.required_values.append("boot/kernel/"+x+"/sources")
				self.required_values.append("boot/kernel/"+x+"/config")
				self.valid_values.append("boot/kernel/"+x+"/aliases")
				self.valid_values.append("boot/kernel/"+x+"/extraversion")
				self.valid_values.append("boot/kernel/"+x+"/packages")
				if addlargs.has_key("boot/kernel/"+x+"/packages"):
					if type(addlargs["boot/kernel/"+x+"/packages"]) == types.StringType:
						addlargs["boot/kernel/"+x+"/packages"]=[addlargs["boot/kernel/"+x+"/packages"]]
				self.valid_values.append("boot/kernel/"+x+"/use")
				self.valid_values.append("boot/kernel/"+x+"/gk_kernargs")
				self.valid_values.append("boot/kernel/"+x+"/gk_action")
				self.valid_values.append("boot/kernel/"+x+"/initramfs_overlay")
				self.valid_values.append("boot/kernel/"+x+"/softlevel")
				self.valid_values.append("boot/kernel/"+x+"/console")
				self.valid_values.append("boot/kernel/"+x+"/machine_type")
				self.valid_values.append("boot/kernel/"+x+"/postconf")
				if addlargs.has_key("boot/kernel/"+x+"/postconf"):
					print "boot/kernel/"+x+"/postconf is deprecated"
					print "\tInternally moving these ebuilds to boot/kernel/"+x+"/packages"
					print "\tPlease move them to boot/kernel/"+x+"/packages in your specfile"
					if type(addlargs["boot/kernel/"+x+"/postconf"]) == types.StringType:
						loop2=[addlargs["boot/kernel/"+x+"/postconf"]]
					else:
						loop2=addlargs["boot/kernel/"+x+"/postconf"]
				
					for y in loop2:
						if not addlargs.has_key("boot/kernel/"+x+"/packages"):
							addlargs["boot/kernel/"+x+"/packages"]=[y]
						else:
							addlargs["boot/kernel/"+x+"/packages"].append(y)

	def set_build_kernel_vars(self):
	    if self.settings.has_key(self.settings["spec_prefix"]+"/devmanager"):
		self.settings["devmanager"]=self.settings[self.settings["spec_prefix"]+"/devmanager"]
		del self.settings[self.settings["spec_prefix"]+"/devmanager"]
	    
	    if self.settings.has_key(self.settings["spec_prefix"]+"/splashtype"):
		self.settings["splashtype"]=self.settings[self.settings["spec_prefix"]+"/splashtype"]
		del self.settings[self.settings["spec_prefix"]+"/splashtype"]
	    
	    if self.settings.has_key(self.settings["spec_prefix"]+"/gk_mainargs"):
		self.settings["gk_mainargs"]=self.settings[self.settings["spec_prefix"]+"/gk_mainargs"]
		del self.settings[self.settings["spec_prefix"]+"/gk_mainargs"]

	def kill_chroot_pids(self):
	    print "Checking for processes running in chroot and killing them."
	    
	    # Force environment variables to be exported so script can see them
	    self.setup_environment()

	    if os.path.exists(self.settings["sharedir"]+"/targets/support/kill-chroot-pids.sh"):
			    cmd("/bin/bash "+self.settings["sharedir"]+"/targets/support/kill-chroot-pids.sh",\
			    			"kill-chroot-pids script failed.",env=self.env)
	
	def mount_safety_check(self):
		mypath=self.settings["chroot_path"]
		
		"""
		check and verify that none of our paths in mypath are mounted. We don't want to clean
		up with things still mounted, and this allows us to check. 
		returns 1 on ok, 0 on "something is still mounted" case.
		"""
		if not os.path.exists(mypath):
			return
		
		for x in self.mounts:
			if not os.path.exists(mypath+x):
				continue
			
			if ismount(mypath+x):
				#something is still mounted
				try:
					print x+" is still mounted; performing auto-bind-umount...",
					# try to umount stuff ourselves
					self.unbind()
					if ismount(mypath+x):
						raise CatalystError, "Auto-unbind failed for "+x
					
					else:
						print "Auto-unbind successful..."
				
				except CatalystError:
					raise CatalystError, "Unable to auto-unbind "+x
		
	def unpack(self):
		unpack=True

		if True:	
			display_msg="\nStarting tar extract from "+self.settings["source_path"]+"\nto "+\
				self.settings["chroot_path"]+" (This may take some time) ...\n"
			unpack_cmd="tar xjpf "+self.settings["source_path"]+" -C "+self.settings["chroot_path"]
			error_msg="Tarball extraction of "+self.settings["source_path"]+" to "+self.settings["chroot_path"]+" failed."
		
		invalid_snapshot=False

		if unpack:
			self.mount_safety_check()
			
			if not os.path.exists(self.settings["chroot_path"]):
				os.makedirs(self.settings["chroot_path"])

			if not os.path.exists(self.settings["chroot_path"]+"/tmp"):
				os.makedirs(self.settings["chroot_path"]+"/tmp",1777)
			
			if self.settings.has_key("PKGCACHE"):	
				if not os.path.exists(self.settings["pkgcache_path"]):
					os.makedirs(self.settings["pkgcache_path"],0755)
			
			if self.settings.has_key("KERNCACHE"):	
				if not os.path.exists(self.settings["kerncache_path"]):
					os.makedirs(self.settings["kerncache_path"],0755)
			
			print display_msg
			cmd(unpack_cmd,error_msg,env=self.env)

		else:
		    print "Resume point detected, skipping unpack operation..."
	

	def unpack_snapshot(self):
		
		destdir=normpath(self.settings["chroot_path"]+"/usr/portage")
		cleanup_errmsg="Error removing existing snapshot directory."
		cleanup_msg="Cleaning up existing portage tree (This can take a long time) ..."
		unpack_cmd="tar xjpf "+self.settings["snapshot_path"]+" -C "+self.settings["chroot_path"]+"/usr"
		unpack_errmsg="Error unpacking snapshot"
	
		if os.path.exists(destdir):
			print cleanup_msg
			cleanup_cmd="rm -rf "+destdir
			cmd(cleanup_cmd,cleanup_errmsg,env=self.env)
		if not os.path.exists(destdir):
			os.makedirs(destdir,0755)
		    	
		print "Unpacking \""+self.settings["portname"]+"\" portage tree "+self.settings["snapshot_path"]+" ..."
		cmd(unpack_cmd,unpack_errmsg,env=self.env)

	def config_profile_link(self):
		print "Configuring profile link..."
		cmd("rm -f "+self.settings["chroot_path"]+"/etc/make.profile",\
				"Error zapping profile link",env=self.env)
		cmd("ln -sf ../usr/portage/profiles/"+self.settings["target_profile"]+\
			" "+self.settings["chroot_path"]+"/etc/make.profile","Error creating profile link",env=self.env)
				       
	def setup_confdir(self):	
		if self.settings.has_key("portage_confdir"):
			print "Configuring /etc/portage..."
			cmd("rm -rf "+self.settings["chroot_path"]+"/etc/portage","Error zapping /etc/portage",env=self.env)
			cmd("cp -R "+self.settings["portage_confdir"]+"/ "+self.settings["chroot_path"]+\
				"/etc/portage","Error copying /etc/portage",env=self.env)
	
	def portage_overlay(self):
	    # Here, we copy the contents of our overlays to /usr/local/portage. We
	    # always copy over the overlays in case it has changed.
	    if self.settings.has_key("portage_overlay"):
		for x in self.settings["portage_overlay"]: 
			if os.path.exists(x):
				print "Copying overlay dir " +x
				cmd("mkdir -p "+self.settings["chroot_path"]+"/usr/local/portage","Could not make portage_overlay dir",env=self.env)
				cmd("cp -R "+x+"/* "+self.settings["chroot_path"]+"/usr/local/portage","Could not copy portage_overlay",env=self.env)
	
	def root_overlay(self):
	    # copy over the root_overlay
	    # Always copy over the overlay incase it has changed
		if self.settings.has_key(self.settings["spec_prefix"]+"/root_overlay"):
			for x in self.settings[self.settings["spec_prefix"]+"/root_overlay"]: 
				if os.path.exists(x):
					print "Copying root_overlay: "+x
					cmd("rsync -a "+x+"/ "+\
						self.settings["chroot_path"], self.settings["spec_prefix"]+"/root_overlay: "+x+" copy failed.",env=self.env)

	def base_dirs(self):
		pass

	def bind(self):
		for x in self.mounts: 
			if not os.path.exists(self.settings["chroot_path"]+x):
				os.makedirs(self.settings["chroot_path"]+x,0755)
			
			if not os.path.exists(self.mountmap[x]):
				os.makedirs(self.mountmap[x],0755)
			
			src=self.mountmap[x]
			if self.settings.has_key("SNAPCACHE") and x == "/usr/portage":
				self.snapshot_lock_object.read_lock()
			if os.uname()[0] == "FreeBSD":
				if src == "/dev":
					retval=os.system("mount -t devfs none "+self.settings["chroot_path"]+x)
				else:
					retval=os.system("mount_nullfs "+src+" "+self.settings["chroot_path"]+x)
			else:
				retval=os.system("mount --bind "+src+" "+self.settings["chroot_path"]+x)
			if retval!=0:
				self.unbind()
				raise CatalystError,"Couldn't bind mount "+src
			    
	
	def unbind(self):
		ouch=0
		mypath=self.settings["chroot_path"]
		myrevmounts=self.mounts[:]
		myrevmounts.reverse()
		# unmount in reverse order for nested bind-mounts
		for x in myrevmounts:
			if not os.path.exists(mypath+x):
				continue
			
			if not ismount(mypath+x):
				# it's not mounted, continue
				continue
			
			retval=os.system("umount "+os.path.join(mypath,x.lstrip(os.path.sep)))
			
			if retval!=0:
				warn("First attempt to unmount: "+mypath+x+" failed.")
				warn("Killing any pids still running in the chroot")
				
				self.kill_chroot_pids()
				
				retval2=os.system("umount "+mypath+x)
				if retval2!=0:
				    ouch=1
				    warn("Couldn't umount bind mount: "+mypath+x)
				    # keep trying to umount the others, to minimize damage if developer makes a mistake
		
			if self.settings.has_key("SNAPCACHE") and x == "/usr/portage":
				try:
				    # Its possible the snapshot lock object isnt created yet
				    # this is because mount safety check calls unbind before the target is fully initialized		
				    self.snapshot_lock_object.unlock()
				except:
				    pass
		if ouch:
			"""
			if any bind mounts really failed, then we need to raise
			this to potentially prevent an upcoming bash stage cleanup script
			from wiping our bind mounts.
			"""
			raise CatalystError,"Couldn't umount one or more bind-mounts; aborting for safety."

	def chroot_setup(self):
		self.makeconf=read_makeconf(self.settings["chroot_path"]+"/etc/make.conf")
		self.override_cbuild()
		self.override_chost()
		self.override_cflags()
		self.override_cxxflags()	
		self.override_ldflags()	
		# drobbins add - envscript doesn't work all the time. This appears to fix it
		print "Writing out proxy settings... (drobbins)"
		try:
			a=open(self.settings["chroot_path"]+"/etc/env.d/99zzcatalyst","w")
		except:
			raise CatalystError,"Couldn't open "+self.settings["chroot_path"]+"/etc/env.d/99zzcatalyst for writing"
		for x in ["http_proxy","ftp_proxy","RSYNC_PROXY"]:
			if os.environ.has_key(x):
				a.write(x+"=\""+os.environ[x]+"\"\n")
			else:
				a.write("# "+x+" is not set")
		a.close()
		if True:	
			print "Setting up chroot..."
			
			#self.makeconf=read_makeconf(self.settings["chroot_path"]+"/etc/make.conf")
			
			cmd("cp /etc/resolv.conf "+self.settings["chroot_path"]+"/etc",\
				"Could not copy resolv.conf into place.",env=self.env)
		
		    # copy over the envscript, if applicable
			if self.settings.has_key("ENVSCRIPT"):
				if not os.path.exists(self.settings["ENVSCRIPT"]):
					raise CatalystError, "Can't find envscript "+self.settings["ENVSCRIPT"]
			    
				print "\nWarning!!!!"
				print "\tOverriding certain env variables may cause catastrophic failure."
				print "\tIf your build fails look here first as the possible problem."
				print "\tCatalyst assumes you know what you are doing when setting"
				print "\t\tthese variables."
				print "\tCatalyst Maintainers use VERY minimal envscripts if used at all"
				print "\tYou have been warned\n"
				
				cmd("cp "+self.settings["ENVSCRIPT"]+" "+self.settings["chroot_path"]+"/tmp/envscript",\
					"Could not copy envscript into place.",env=self.env)

			# Setup metadata_overlay
			if self.settings.has_key("METADATA_OVERLAY") and not self.settings.has_key("portage_confdir"):
				if not os.path.exists(self.settings["chroot_path"] + "/etc/portage"):
					cmd("mkdir " + self.settings["chroot_path"] + "/etc/portage")
				myf = open(self.settings["chroot_path"] + "/etc/portage/modules", "a")
				myf.write("portdbapi.auxdbmodule = cache.metadata_overlay.database\n")
				myf.close()

		    # Copy over /etc/hosts from the host in case there are any
			# specialties in there
			if os.path.exists(self.settings["chroot_path"]+"/etc/hosts"):
				cmd("mv "+self.settings["chroot_path"]+"/etc/hosts "+self.settings["chroot_path"]+\
					"/etc/hosts.bck", "Could not backup /etc/hosts",env=self.env)
				cmd("cp /etc/hosts "+self.settings["chroot_path"]+"/etc/hosts", "Could not copy /etc/hosts",env=self.env)
			#self.override_cbuild()
			#self.override_chost()
			#self.override_cflags()
			#self.override_cxxflags()	
			#self.override_ldflags()	
			# Modify and write out make.conf (for the chroot)
			cmd("rm -f "+self.settings["chroot_path"]+"/etc/make.conf","Could not remove "+self.settings["chroot_path"]+"/etc/make.conf",\
				env=self.env)
			myf=open(self.settings["chroot_path"]+"/etc/make.conf","w")
			myf.write("# These settings were set by the catalyst build script that automatically\n# built this stage.\n")
			myf.write("# Please consult /etc/make.conf.example for a more detailed example.\n")
			if self.settings.has_key("CFLAGS"):
				myf.write('CFLAGS="'+self.settings["CFLAGS"]+'"\n')
			if self.settings.has_key("CXXFLAGS"):
				myf.write('CXXFLAGS="'+self.settings["CXXFLAGS"]+'"\n')
			else:
				myf.write('CXXFLAGS="${CFLAGS}"\n')
		    
			if self.settings.has_key("LDFLAGS"):
				myf.write('LDFLAGS="'+self.settings["LDFLAGS"]+'"\n')
			myf.write("# This should not be changed unless you know exactly what you are doing.  You\n# should probably be using a different stage, instead.\n")
			if self.settings.has_key("CBUILD"):
				myf.write('CBUILD="'+self.settings["CBUILD"]+'"\n')
			myf.write('# WARNING: Changing your CHOST is not something that should be done lightly.\n# Please consult http://www.gentoo.org/doc/en/change-chost.xml before changing it.\nCHOST="'+self.settings["CHOST"]+'"\n')
			# unconditionally set ACCEPT_KEYWORDS as it serves as documentation on how the build was done even if a default value is used like "amd64", "x86", etc.
			myf.write('ACCEPT_KEYWORDS="'+self.settings["treearch"]+'"\n')
			print "DEBUG: ACCEPT_KEYWORDS=\""+self.settings["treearch"]+'"'
		    # Figure out what our USE vars are for building
			myusevars=[]
			if self.settings.has_key("HOSTUSE"):
				myusevars.extend(self.settings["HOSTUSE"])
		
			if self.settings.has_key("use"):
				myusevars.extend(self.settings["use"])
				myf.write('USE="'+string.join(myusevars)+'"\n')

		    # Setup the portage overlay	
			if self.settings.has_key("portage_overlay"):
#				myf.write('PORTDIR_OVERLAY="'+string.join(self.settings["portage_overlay"])+'"\n')
				myf.write('PORTDIR_OVERLAY="/usr/local/portage"\n')

			myf.close()
	
	def fsscript(self):
		if os.path.exists(self.settings["controller_file"]):
    			cmd("/bin/bash "+self.settings["controller_file"]+" fsscript","fsscript script failed.",env=self.env)

	def rcupdate(self):
		if os.path.exists(self.settings["controller_file"]):
			cmd("/bin/bash "+self.settings["controller_file"]+" rc-update","rc-update script failed.",env=self.env)

	def clean(self):
		# drobbins add
	    	if self.settings["destpath"] == self.settings["chroot_path"]:
		# clean up possibly sensitive proxy settings that we set up in the chroot
			for x in ["/etc/profile.env","/etc/csh.env","/etc/env.d/99zzcatalyst"]:
				if os.path.exists(self.settings["chroot_path"]+x):
					print "Cleaning chroot: "+x+"... " 
					cmd("rm -f "+self.settings["chroot_path"]+x)
		# drobbins add end
		for x in self.settings["cleanables"]: 
			print "Cleaning chroot: "+x+"... "
			cmd("rm -rf "+self.settings["destpath"]+x,"Couldn't clean "+x,env=self.env)

		# put /etc/hosts back into place
		if os.path.exists(self.settings["chroot_path"]+"/etc/hosts.bck"):
			cmd("mv -f "+self.settings["chroot_path"]+"/etc/hosts.bck "+self.settings["chroot_path"]+"/etc/hosts", "Could not replace /etc/hosts",env=self.env)

		# remove our overlay
		if os.path.exists(self.settings["chroot_path"]+"/usr/local/portage"):
			cmd("rm -rf "+self.settings["chroot_path"]+"/usr/local/portage", "Could not remove /usr/local/portage",env=self.env)
			cmd("sed -i '/^PORTDIR_OVERLAY/d' "+self.settings["chroot_path"]+"/etc/make.conf", "Could not remove PORTDIR_OVERLAY from make.conf",env=self.env)

		# clean up old and obsoleted files in /etc
		if os.path.exists(self.settings["stage_path"]+"/etc"):
			cmd("find "+self.settings["stage_path"]+"/etc -maxdepth 1 -name \"*-\" | xargs rm -f", "Could not remove stray files in /etc",env=self.env)

		if os.path.exists(self.settings["controller_file"]):
			cmd("/bin/bash "+self.settings["controller_file"]+" clean","clean script failed.",env=self.env)
	
	def empty(self):		
		if self.settings.has_key(self.settings["spec_prefix"]+"/empty"):
		    if type(self.settings[self.settings["spec_prefix"]+"/empty"])==types.StringType:
			self.settings[self.settings["spec_prefix"]+"/empty"]=self.settings[self.settings["spec_prefix"]+"/empty"].split()
		    for x in self.settings[self.settings["spec_prefix"]+"/empty"]:
			myemp=self.settings["destpath"]+x
			if not os.path.isdir(myemp):
			    print x,"not a directory or does not exist, skipping 'empty' operation."
			    continue
			print "Emptying directory",x
			# stat the dir, delete the dir, recreate the dir and set
			# the proper perms and ownership
			mystat=os.stat(myemp)
			shutil.rmtree(myemp)
			os.makedirs(myemp,0755)
			os.chown(myemp,mystat[ST_UID],mystat[ST_GID])
			os.chmod(myemp,mystat[ST_MODE])
	
	def remove(self):
		if self.settings.has_key(self.settings["spec_prefix"]+"/rm"):
		    for x in self.settings[self.settings["spec_prefix"]+"/rm"]:
			# we're going to shell out for all these cleaning operations,
			# so we get easy glob handling
			print "livecd: removing "+x
			os.system("rm -rf "+self.settings["chroot_path"]+x)
		try:
		    if os.path.exists(self.settings["controller_file"]):
			    cmd("/bin/bash "+self.settings["controller_file"]+" clean",\
				"Clean  failed.",env=self.env)
		except:
		    self.unbind()
		    raise

	
	def preclean(self):
		try:
			if os.path.exists(self.settings["controller_file"]):
		    		cmd("/bin/bash "+self.settings["controller_file"]+" preclean","preclean script failed.",env=self.env)
		
		except:
			self.unbind()
			raise CatalystError, "Build failed, could not execute preclean"

	def capture(self):
		"""capture target in a tarball"""
		mypath=self.settings["target_path"].split("/")
		# remove filename from path
		mypath=string.join(mypath[:-1],"/")
		
		# now make sure path exists
		if not os.path.exists(mypath):
			os.makedirs(mypath)

		print "Creating stage tarball..."
		
		cmd("tar cjpf "+self.settings["target_path"]+" -C "+self.settings["stage_path"]+\
			" .","Couldn't create stage tarball",env=self.env)


	def run_local(self):
		try:
			if os.path.exists(self.settings["controller_file"]):
		    		cmd("/bin/bash "+self.settings["controller_file"]+" run","run script failed.",env=self.env)

		except CatalystError:
			self.unbind()
			raise CatalystError,"Stage build aborting due to error."
	
	def setup_environment(self):
		# Modify the current environment. This is an ugly hack that should be
		# fixed. We need this to use the os.system() call since we can't
		# specify our own environ:
		for x in self.settings.keys():
			# sanitize var names by doing "s|/-.|_|g"
			varname="clst_"+string.replace(x,"/","_")
			varname=string.replace(varname,"-","_")
			varname=string.replace(varname,".","_")
			if type(self.settings[x])==types.StringType:
				# prefix to prevent namespace clashes:
				#os.environ[varname]=self.settings[x]
				self.env[varname]=self.settings[x]
			elif type(self.settings[x])==types.ListType:
				#os.environ[varname]=string.join(self.settings[x])
				self.env[varname]=string.join(self.settings[x])
			elif type(self.settings[x])==types.BooleanType:
				if self.settings[x]:
					self.env[varname]="true"
				else:
					self.env[varname]="false"
		if self.settings.has_key("makeopts"):
			self.env["MAKEOPTS"]=self.settings["makeopts"]
			
	def run(self):
		self.chroot_lock.write_lock()

                # Kill any pids in the chroot
                self.kill_chroot_pids()

                # Check for mounts right away and abort if we cannot unmount them.
                self.mount_safety_check()

                if self.settings.has_key("PURGE"):
                        self.purge()

		for x in self.settings["action_sequence"]:
			print "--- Running action sequence: "+x
			sys.stdout.flush()
			try:
				apply(getattr(self,x))
			except:
				self.mount_safety_check()
				raise
		
		self.chroot_lock.unlock()

        def unmerge(self):
		if self.settings.has_key(self.settings["spec_prefix"]+"/unmerge"):
		    if type(self.settings[self.settings["spec_prefix"]+"/unmerge"])==types.StringType:
			self.settings[self.settings["spec_prefix"]+"/unmerge"]=[self.settings[self.settings["spec_prefix"]+"/unmerge"]]
		    myunmerge=self.settings[self.settings["spec_prefix"]+"/unmerge"][:]
		    
		    for x in range(0,len(myunmerge)):
		    #surround args with quotes for passing to bash,
		    #allows things like "<" to remain intact
		        myunmerge[x]="'"+myunmerge[x]+"'"
		    myunmerge=string.join(myunmerge)
		    
		    #before cleaning, unmerge stuff:
		    try:
			cmd("/bin/bash "+self.settings["controller_file"]+" unmerge "+ myunmerge,\
				"Unmerge script failed.",env=self.env)
			#cmd("/bin/bash "+self.settings["sharedir"]+"/targets/" \
			#	+self.settings["target"]+"/unmerge.sh "+myunmerge,"Unmerge script failed.",env=self.env)
			print "unmerge shell script"
		    except CatalystError:
			self.unbind()
			raise


	def target_setup(self):
		print "Setting up filesystems per filesystem type"
		cmd("/bin/bash "+self.settings["controller_file"]+" target_image_setup "+ self.settings["target_path"],\
				"target_image_setup script failed.",env=self.env)
	
	def setup_overlay(self):	
		if self.settings.has_key(self.settings["spec_prefix"]+"/overlay"):
			for x in self.settings[self.settings["spec_prefix"]+"/overlay"]: 
				if os.path.exists(x):
					cmd("rsync -a "+x+"/ "+\
						self.settings["target_path"], self.settings["spec_prefix"]+"overlay: "+x+" copy failed.",env=self.env)
	
	def create_iso(self):
		# create the ISO - this is the preferred method (the iso scripts do not always work)
		if self.settings.has_key("iso"):
			cmd("/bin/bash "+self.settings["controller_file"]+" iso "+\
				self.settings["iso"],"ISO creation script failed.",env=self.env)
		else:
			print "WARNING livecd/iso was not defined."
			print "A CD Image will not be created, skipping create-iso.sh..."

        def build_packages(self):
		if self.settings.has_key(self.settings["spec_prefix"]+"/packages"):
			mypack=list_bashify(self.settings[self.settings["spec_prefix"]+"/packages"])
			try:
				cmd("/bin/bash "+self.settings["controller_file"]+\
					" build_packages "+mypack,"Error in attempt to build packages",env=self.env)
			except CatalystError:
				self.unbind()
				raise CatalystError,self.settings["spec_prefix"] + "build aborting due to error."
	
	def build_kernel(self):
		if True:
			if self.settings.has_key("boot/kernel"):
				try:
					mynames=self.settings["boot/kernel"]
					if type(mynames)==types.StringType:
						mynames=[mynames]
					# execute the script that sets up the kernel build environment
					cmd("/bin/bash "+self.settings["controller_file"]+" pre-kmerge ",\
						"Runscript pre-kmerge failed",env=self.env)
		
					for kname in mynames:
						if True:	
							try:
								if not os.path.exists(self.settings["boot/kernel/"+kname+"/config"]):
									self.unbind()
									raise CatalystError, "Can't find kernel config: " \
										+self.settings["boot/kernel/"+kname+"/config"]

							except TypeError:
								raise CatalystError, "Required value boot/kernel/config not specified"
			
							try:
								cmd("cp "+self.settings["boot/kernel/"+kname+"/config"]+" "+ \
									self.settings["chroot_path"]+"/var/tmp/"+kname+".config", \
									"Couldn't copy kernel config: "+self.settings["boot/kernel/"+kname+"/config"],\
									env=self.env)

							except CatalystError:
								self.unbind()

							# If we need to pass special options to the bootloader
							# for this kernel put them into the environment.
							if self.settings.has_key("boot/kernel/"+kname+"/kernelopts"):
								myopts=self.settings["boot/kernel/"+kname+"/kernelopts"]
				
								if type(myopts) != types.StringType:
									myopts = string.join(myopts)
									self.env[kname+"_kernelopts"]=myopts

								else:
									self.env[kname+"_kernelopts"]=""
					    
							if not self.settings.has_key("boot/kernel/"+kname+"/extraversion"):
								self.settings["boot/kernel/"+kname+"/extraversion"]=""
						
							self.env["clst_kextraversion"]=self.settings["boot/kernel/"+kname+"/extraversion"]

							if self.settings.has_key("boot/kernel/"+kname+"/initramfs_overlay"):
								if os.path.exists(self.settings["boot/kernel/"+kname+"/initramfs_overlay"]):
									print "Copying initramfs_overlay dir " +self.settings["boot/kernel/"+kname+"/initramfs_overlay"]

									cmd("mkdir -p "+self.settings["chroot_path"]+"/tmp/initramfs_overlay/" + \
										self.settings["boot/kernel/"+kname+"/initramfs_overlay"],env=self.env)
						
									cmd("cp -R "+self.settings["boot/kernel/"+kname+"/initramfs_overlay"]+"/* " + \
										self.settings["chroot_path"] + "/tmp/initramfs_overlay/" + \
										self.settings["boot/kernel/"+kname+"/initramfs_overlay"],\
										env=self.env)
	

							# execute the script that builds the kernel
							cmd("/bin/bash "+self.settings["controller_file"]+" kernel "+kname,\
								"Runscript kernel build failed",env=self.env)
					
							if self.settings.has_key("boot/kernel/"+kname+"/initramfs_overlay"):
								if os.path.exists(self.settings["chroot_path"]+"/tmp/initramfs_overlay/"):
									print "Cleaning up temporary overlay dir"
									cmd("rm -R "+self.settings["chroot_path"]+"/tmp/initramfs_overlay/",env=self.env)


							# execute the script that cleans up the kernel build environment
							cmd("/bin/bash "+self.settings["controller_file"]+" post-kmerge ",\
								"Runscript post-kmerge failed",env=self.env)
				
			
				except CatalystError:
					self.unbind()
					raise CatalystError,"build aborting due to kernel build error."

	def bootloader(self):
		try:
			cmd("/bin/bash "+self.settings["controller_file"]+" bootloader " + self.settings["target_path"],\
				"Bootloader runscript failed.",env=self.env)
		except CatalystError:
			self.unbind()
			raise CatalystError,"Runscript aborting due to error."

        def livecd_update(self):
		try:
			cmd("/bin/bash "+self.settings["controller_file"]+" livecd-update",\
				"livecd-update failed.",env=self.env)
		
		except CatalystError:
			self.unbind()
			raise CatalystError,"build aborting due to livecd_update error."

	def clear_chroot(self):
		myemp=self.settings["chroot_path"]
		if os.path.isdir(myemp):
		    print "Emptying directory",myemp
		    # stat the dir, delete the dir, recreate the dir and set
		    # the proper perms and ownership
		    mystat=os.stat(myemp)
		    #cmd("rm -rf "+myemp, "Could not remove existing file: "+myemp,env=self.env)
		    if os.uname()[0] == "FreeBSD": # There's no easy way to change flags recursively in python
			    os.system("chflags -R noschg "+myemp)
		    shutil.rmtree(myemp)
		    os.makedirs(myemp,0755)
		    os.chown(myemp,mystat[ST_UID],mystat[ST_GID])
		    os.chmod(myemp,mystat[ST_MODE])
	
	def clear_packages(self):
	    if self.settings.has_key("PKGCACHE"):
		print "purging the pkgcache ..."

		myemp=self.settings["pkgcache_path"]
		if os.path.isdir(myemp):
		    print "Emptying directory",myemp
		    # stat the dir, delete the dir, recreate the dir and set
		    # the proper perms and ownership
		    mystat=os.stat(myemp)
		    #cmd("rm -rf "+myemp, "Could not remove existing file: "+myemp,env=self.env)
		    shutil.rmtree(myemp)
		    os.makedirs(myemp,0755)
		    os.chown(myemp,mystat[ST_UID],mystat[ST_GID])
		    os.chmod(myemp,mystat[ST_MODE])
	
	def clear_kerncache(self):
	    if self.settings.has_key("KERNCACHE"):
		print "purging the kerncache ..."

		myemp=self.settings["kerncache_path"]
		if os.path.isdir(myemp):
		    print "Emptying directory",myemp
		    # stat the dir, delete the dir, recreate the dir and set
		    # the proper perms and ownership
		    mystat=os.stat(myemp)
		    #cmd("rm -rf "+myemp, "Could not remove existing file: "+myemp,env=self.env)
		    shutil.rmtree(myemp)
		    os.makedirs(myemp,0755)
		    os.chown(myemp,mystat[ST_UID],mystat[ST_GID])
		    os.chmod(myemp,mystat[ST_MODE])
	
	def purge(self):
	    countdown(10,"Purging Caches ...")
	    if self.settings.has_key("PURGE"):
		print "clearing chroot ..."
		self.clear_chroot()
		
		print "clearing package cache ..."
		self.clear_packages()
		
		print "clearing kerncache ..."
		self.clear_kerncache()

#vim: ts=4 sw=4 sta et sts=4 ai
