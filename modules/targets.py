import os,string,imp,types,shutil
from catalyst_support import *
from stat import *
import os

class target:

	def checkconfig(self,strict=True):

		# notify user of any variable that were accessed but were not defined:
		self.settings.expand_all()

		failcount = 0
		if strict:
			warnmsg = "ERROR: "
		else:
			warnmsg = "Warning: "
	
		for element in self.settings.blanks.keys():
			print warnmsg+"value \""+element+"\" was referenced but not defined."
			failcount += 1
		if strict and failcount:
			raise MetroError, "Total config errors: "+`failcount`+" - stopping."

	def require(self,mylist):
		missing=self.settings.missing(mylist)
		if missing:
			raise MetroError,"Missing required configuration values "+`missing`

	def recommend(self,mylist):
		missing=self.settings.missing(mylist)
		for item in missing:
			print "Warning: recommended value \""+item+"\" not defined."

	def bin(self,myc):
		"""look through the environmental path for an executable file named whatever myc is"""
		# this sucks. badly.
		p=self.env["PATH"]
		for x in p.split(":"):
			#if it exists, and is executable
			if os.path.exists("%s/%s" % (x,myc)) and os.stat("%s/%s" % (x,myc))[0] & 0x0248:
				return "%s/%s" % (x,myc)
		raise MetroError, "Can't find command "+myc

	def __init__(self,settings):
	
		self.settings = settings
		self.env = {}
		self.env["PATH"] = "/bin:/sbin:/usr/bin:/usr/sbin"

		self.require(["target","version"])

		if not os.path.exists(self.settings["workdir"]):
			os.makedirs(self.settings["workdir"])

	def cleanup(self):
		if os.path.exists(self.settings["workdir"]):
			print "Cleaning up "+self.settings["workdir"]+"..."
		self.cmd(self.bin("rm") + " -rf "+self.settings["workdir"])

	def cmd(self,mycmd,myexc="",badval=None):
		print "Executing \""+mycmd+"\"..."
		#print "Executing \""+mycmd.split(" ")[0]+"\"..."
		try:
			sys.stdout.flush()
			retval=spawn_bash(mycmd,self.env)
			if badval:
				# This code is here because tar has a retval of 1 for non-fatal warnings
				if retval == badval:
					raise MetroError,myexc
			else:
				if retval != 0:
					raise MetroError,myexc
		except:
			raise

class chroot(target):

	def kill_chroot_pids(self):
		cdir=self.settings["chrootdir"]
		for pid in os.listdir("/proc"):
			if not os.path.isdir("/proc/"+pid):
				continue
			try:
				mylink = os.readlink("/proc/"+pid+"/exe")
			except OSError:
				# not a pid directory
				continue
			if mylink[0:len(cdir)] == cdir:
				#we got something in our chroot
				print "Killing process "+pid+" ("+mylink+")"
				self.cmd("/bin/kill -9 "+pid)

	def exec_in_chroot(self,key,chrootdir=None):

		if chrootdir == None:
			chrootdir = self.settings["chrootdir"]

		print "Running "+repr(key)+" in "+chrootdir+"..."

		if not self.settings.has_key(key):
			raise MetroError, "exec_in_chroot: key \""+key+"\" not found."
	
		if type(self.settings[key]) != types.ListType:
			raise MetroError, "exec_in_chroot: key \""+key+"\" is not a multi-line element."

		outfile = chrootdir+"/tmp/"+key+".sh"
		outdir = os.path.dirname(outfile)

		if not os.path.exists(outdir):
			os.makedirs(outdir)
		outfd = open(outfile,"w")
		
		for x in self.settings[key]:
			outfd.write(x+"\n")

		outfd.close()

		if self.settings["arch"] == "x86" and os.uname()[4] == "x86_64":
			cmds = [self.bin("linux32"),self.bin("chroot"),chrootdir,self.bin("bash")]
		else:
			cmds = [self.bin("chroot"),chrootdir,self.bin("bash")]

		cmds.append("/tmp/"+key+".sh")

		retval = spawn(cmds, env=self.env )

		if retval != 0:
			raise MetroError, "Command failure: "+" ".join(cmds)

	def __init__(self,settings):
		target.__init__(self,settings)

		# DEFINE GENERAL LINUX CHROOT MOUNTS

		self.mounts=[ "/proc" ]
		self.mountmap={"/proc":"/proc" }
		
		# CCACHE SUPPORT FOR CHROOTS

		if self.settings.has_key("options") and "ccache" in self.settings["options"].split():
			if os.environ.has_key("CCACHE_DIR"):
				ccdir=os.environ["CCACHE_DIR"]
			else:
				ccdir="/root/.ccache"
			if not os.path.isdir(ccdir):
					raise MetroError, "Compiler cache support can't be enabled (can't find "+ccdir+")"
			self.mounts.append("/var/tmp/ccache")
			self.mountmap["/var/tmp/ccache"]=ccdir
	
	def bind(self):
		""" Perform bind mounts """
		for x in self.mounts: 
			if not os.path.exists(self.settings["chrootdir"]+x):
				os.makedirs(self.settings["chrootdir"]+x,0755)
			
			if not os.path.exists(self.mountmap[x]):
				os.makedirs(self.mountmap[x],0755)
			
			src=self.mountmap[x]
			if os.system("/bin/mount --bind "+src+" "+self.settings["chrootdir"]+x) != 0:
				self.unbind()
				raise MetroError,"Couldn't bind mount "+src
			    
	
	def unbind(self):
		""" Attempt to unmount bind mounts"""
		ouch=0
		mypath=self.settings["chrootdir"]
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
		if ouch:
			"""
			if any bind mounts really failed, then we need to raise
			this to potentially prevent an upcoming bash stage cleanup script
			from wiping our bind mounts.
			"""
			raise MetroError,"Couldn't umount one or more bind-mounts; aborting for safety."

	def mount_safety_check(self):
		mypath=self.settings["chrootdir"]
		
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
						raise MetroError, "Auto-unbind failed for "+x
					else:
						print "Auto-unbind successful..."
				except MetroError:
					raise MetroError, "Unable to auto-unbind "+x

class snapshot(target):
	def __init__(self,settings):
		target.__init__(self,settings)

		if os.path.exists("/etc/metro/snapshot.spec"):
			print "Reading in configuration from /etc/metro/snapshot.spec..."
			self.settings.collect("/etc/metro/snapshot.spec")

		self.require(["snapshot/type","portname","snapshot/path","version","target"])
		self.require(["storedir/snapshot"])

		if self.settings["snapshot/type"] == "git":
			self.require(["snapshot/branch"])

	def run(self):

		if os.path.exists(self.settings["workdir"]):
			print "Removing existing temporary work directory..."
			self.cmd( self.bin("rm") + " -rf " + self.settings["workdir"] )
			os.makedirs(self.settings["workdir"])

		if "replace" in self.settings["options"].split():
			if os.path.exists(self.settings["storedir/snapshot"]):
				print "Removing existing snapshot..."
				self.cmd( self.bin("rm") + " -f " + self.settings["storedir/snapshot"])

		elif os.path.exists(self.settings["storedir/snapshot"]):
			print "Snapshot already exists at "+self.settings["storedir/snapshot"]+". Skipping..."
			return
		else:
			print self.settings["storedir/snapshot"],"does not exist - creating it..."

		# TODO - add check to ensure that run/rysnc or run/git has been defined, here or in constructor
		self.exec("run/"+self.settings["snapshot/type"])
		#raise MetroError, "snapshot/type of \""+self.settings["snapshot/type"]+"\" not recognized."
		# workdir cleanup is handled by catalyst calling our cleanup() method

class stage(chroot):

	def __init__(self,settings):
		chroot.__init__(self,settings)

		if os.path.exists("/etc/metro/stage.spec"):
			print "Reading in configuration from /etc/metro/stage.spec..."
			self.settings.collect("/etc/metro/stage.spec")

		# In the constructor, we want to define settings but not reference them if we can help it, certain things
		# like paths may not be able to be fully expanded yet until we define our goodies like "source", etc.

		self.require(["ROOT","target","source","arch","subarch","profile","storedir/srcstage","storedir/deststage","storedir/snapshot","CHOST"])
		
		# If distdir, USE or CFLAGS not specified, alert the user that they might be missing them
		self.recommend(["distdir","USE","CFLAGS","MAKEOPTS"])

		# DEFINE GENTOO MOUNTS

		if self.settings.has_key("distdir"):
			self.mounts.append("/usr/portage/distfiles")
			self.mountmap["/usr/portage/distfiles"]=self.settings["distdir"]

		self.settings["chrootdir"]="$[workdir]/chroot"

		if self.settings["ROOT"] != "/":
			# this seems to be needed for libperl to build (x2p) during stage1 - so we'll mount it....
			self.mounts.append("/dev")
			self.mounts.append("/dev/pts")
			self.mountmap["/dev"] = "/dev"
			self.mountmap["/dev/pts"] = "/dev/pts"


	def run(self):

		if "replace" in self.settings["options"].split():
			if os.path.exists(settings["storedir/deststage"]):
				print "Removing existing stage..."
				self.cmd( self.bin("rm") + " -f " + self.settings["storedir/deststage"])
		# do not overwrite snapshot if it already exists
		elif os.path.exists(self.settings["storedir/deststage"]):
			print "Stage "+repr(self.settings["storedir/deststage"])+" already exists - skipping..."
			return
			#raise MetroError,"Snapshot "+self.settings["storedir/snapshot"]+" already exists. Aborting."

		# look for required files
		for loc in [ "storedir/srcstage", "storedir/snapshot" ]:
			if not os.path.exists(self.settings[loc]):
				raise MetroError,"Required file "+self.settings[loc]+" not found. Aborting."

		# BEFORE WE CLEAN UP - MAKE SURE WE ARE UNMOUNTED
		self.kill_chroot_pids()
		self.mount_safety_check()

		# BEFORE WE START - CLEAN UP ANY MESSES
		if os.path.exists(self.settings["workdir"]):
			print "Removing existing temporary work directory..."
			self.cmd( self.bin("rm") + " -rf " + self.settings["workdir"] )
		try:
			self.mount_safety_check()
			self.exec("unpack")
			self.exec("unpack/post")
			self.unpack_snapshot()

			self.bind()

			self.exec_in_chroot("chroot/prerun")
			self.exec_in_chroot("chroot/run")
			self.exec_in_chroot("chroot/postrun")
			
			self.unbind()
			
			# remove our tweaks...

			self.chroot_cleanup()

			# now let the spec-defined clean script do all the heavy lifting...

			if self.settings["target"] == "stage1":
				self.exec_in_chroot("chroot/clean",self.settings["chrootdir"]+self.settings["ROOT"])
			else:
				self.exec_in_chroot("chroot/clean")
			
		except:
		
			self.kill_chroot_pids()
			self.mount_safety_check()
			raise

		# Now, grab the fruits of our labor.
		self.capture()
	
	def capture(self):
		"""capture target in a tarball"""
		# IF TARGET EXISTS, REMOVE IT - WE WILL CREATE A NEW ONE
		if os.path.exists(self.settings["storedir/deststage"]):
			if os.path.isfile(self.settings["storedir/deststage"]):
				self.cmd("rm -f "+self.settings["storedir/deststage"], "Could not remove existing file: "+self.settings["storedir/deststage"])
			else:
				raise MetroError,"Can't remove existing "+self.settings["storedir/deststage"]+" - not a file. Aborting."

		grabpath=os.path.normpath(self.settings["chrootdir"]+self.settings["ROOT"])
		
		# Ensure target stage directory exists (might be several subdirectories that need to be created)
		if not os.path.exists(os.path.dirname(self.settings["storedir/deststage"])):
			os.makedirs(os.path.dirname(self.settings["storedir/deststage"]))

		print "Creating stage tarball..."
		self.cmd("tar cjpf "+self.settings["storedir/deststage"]+" -C "+grabpath+" .","Couldn't create stage tarball",badval=2)

#vim: ts=4 sw=4 sta et sts=4 ai
