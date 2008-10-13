import os,string,imp,types,shutil
from catalyst_support import *
from stat import *
import os

bin={
	"linux32": "/usr/bin/linux32",
	"rm": "/bin/rm",
	"chroot": "/usr/bin/chroot",
	"bash": "/bin/bash",
	"mount": "/bin/mount",
	"kill":"/bin/kill",
	"install":"/usr/bin/install"
}

class target:

	def runScript(self,key,chroot=None):
		if not self.settings.has_key(key):
			raise MetroError, "exec: key \""+key+"\" not found."
		if type(self.settings[key]) != types.ListType:
			raise MetroError, "exec: key \""+key+"\" is not a multi-line element."

		os.environ["PATH"] = self.env["PATH"]

		if chroot:
			chrootfile = "/tmp/"+key+".metro"
			outfile = chroot+chrootfile
		else:
			outfile = self.settings["path/tmp"]+"/pid/"+repr(os.getpid())

		outdir = os.path.dirname(outfile)

		if not os.path.exists(outdir):
			os.makedirs(outdir)
		outfd = open(outfile,"w")
		
		for x in self.settings[key]:
			outfd.write(x+"\n")

		outfd.close()
		# make executable:
		os.chmod(outfile, 0755)

		cmds = []
		if chroot:
			if self.settings["subarch/arch"] == "x86" and os.uname()[4] == "x86_64":
				cmds = [bin["linux32"],bin["chroot"]]
			else:
				cmds = [bin["chroot"]]
			cmds.append(chrootfile)
		else:
			cmds.append(outfile)

		retval = spawn(cmds, env=self.env )

		if retval != 0:
			raise MetroError, "Command failure: "+" ".join(cmds)


	def targetExists(self,key):
		if "replace" in self.settings["metro/options"].split():
			if os.path.exists(settings[key]):
				print "Removing existing file %s..." % self.settings[key]
				self.cmd( bin["rm"] + " -f " + self.settings[key])
			return False
		elif os.path.exists(self.settings[key]):
			print "File %s already exists - skipping..." % self.settings[key]
			return True
		else:
			return False

	def require(self,mylist):
		missing=self.settings.missing(mylist)
		if missing:
			raise MetroError,"Missing required configuration values "+`missing`

	def recommend(self,mylist):
		missing=self.settings.missing(mylist)
		for item in missing:
			print "Warning: recommended value \""+item+"\" not defined."

	def __init__(self,settings):
		self.settings = settings
		self.env = {}
		self.env["PATH"] = "/bin:/sbin:/usr/bin:/usr/sbin"

	def cleanPath(self,path=None,recreate=False):
		if path == None:
			path = self.settings["path/work"]
		if os.path.exists(path):
			print "Cleaning up %s..." % path
		self.cmd(bin["rm"]+" -rf "+path)
		if recreate:
			self.cmd(bin["install"]+" -d "+path)

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
		cdir=self.settings["path/work"]
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
				self.cmd(bin["kill"]+" -9 "+pid)

	def runScriptInChroot(self,key,chrootdir=None):
		if chrootdir == None:
			return self.runScript(key,chrootdir=self.settings["path/work"])
		else:
			return self.runScript(key,chrootdir)

	def __init__(self,settings):
		target.__init__(self,settings)

		# DEFINE GENERAL LINUX CHROOT MOUNTS

		self.mounts=[ "/proc" ]
		self.mountmap={"/proc":"/proc" }
		
		# CCACHE SUPPORT FOR CHROOTS

		if self.settings.has_key("metro/options") and "ccache" in self.settings["metro/options"].split():
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
			if not os.path.exists(self.settings["path/work"]+x):
				os.makedirs(self.settings["path/work"]+x,0755)
			
			if not os.path.exists(self.mountmap[x]):
				os.makedirs(self.mountmap[x],0755)
			
			src=self.mountmap[x]
			if os.system(bin["mount"]+" --bind "+src+" "+self.settings["path/work"]+x) != 0:
				self.unbind()
				raise MetroError,"Couldn't bind mount "+src
			    
	
	def unbind(self):
		""" Attempt to unmount bind mounts"""
		ouch=0
		mypath=self.settings["path/work"]
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
		mypath=self.settings["path/work"]
		
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
	
	def run(self):
		if self.targetExists("path/mirror/snapshot"):
			return

		self.cleanPath(recreate=True)

		runkey="steps/run/"+self.settings["target/type"]

		if not self.settings.has_key(runkey):
			raise MetroError, "Required steps in %s not found." % runkey

		self.runScript(runkey)

class stage(chroot):

	def __init__(self,settings):
		chroot.__init__(self,settings)

		# DEFINE GENTOO MOUNTS
		if self.settings.has_key("path/distfiles"):
			self.mounts.append("/usr/portage/distfiles")
			self.mountmap["/usr/portage/distfiles"]=self.settings["path/distfiles"]

		if self.settings["ROOT"] != "/":
			# this seems to be needed for libperl to build (x2p) during stage1 - so we'll mount it....
			self.mounts.append("/dev")
			self.mounts.append("/dev/pts")
			self.mountmap["/dev"] = "/dev"
			self.mountmap["/dev/pts"] = "/dev/pts"
	def run(self):
		if self.targetExists("path/mirror/deststage"):
			return

		# look for required files
		for loc in [ "path/mirror/srcstage", "path/mirror/snapshot" ]:
			if not os.path.exists(self.settings[loc]):
				raise MetroError,"Required file "+self.settings[loc]+" not found. Aborting."

		# BEFORE WE CLEAN UP - MAKE SURE WE ARE UNMOUNTED
		self.kill_chroot_pids()
		self.mount_safety_check()

		# BEFORE WE START - CLEAN UP ANY MESSES
		self.cleanPath(recreate=True)
		try:
			self.mount_safety_check()
			self.runScript("steps/unpack")
			if self.settings.has_key("steps/unpack/post"):
				self.runScript("steps/unpack/post")

			self.bind()

			self.runScriptInChroot("steps/prerun")
			self.runScriptInChroot("steps/run")
			self.runScriptInChroot("steps/postrun")
			
			self.unbind()
			
			# remove our tweaks...

			self.chroot_cleanup()

			# now let the spec-defined clean script do all the heavy lifting...
			# NEED A VARIABLE FOR THE "REAL" CHROOT:	
			self.runScriptInChroot("steps/clean")
			
		except:
		
			self.kill_chroot_pids()
			self.mount_safety_check()
			raise

		# Now, grab the fruits of our labor.
		self.capture()
	
	def capture(self):
		"""capture target in a tarball"""
		# target should not exist - we removed it earlier if it did
		grabpath=os.path.normpath(self.settings["path/work"]+self.settings["ROOT"])
		
		# Ensure target stage directory exists (might be several subdirectories that need to be created)
		if not os.path.exists(os.path.dirname(self.settings["path/mirror/deststage"])):
			os.makedirs(os.path.dirname(self.settings["path/mirror/deststage"]))

		print "Creating stage tarball..."
		self.cmd("tar cjpf "+self.settings["path/mirror//deststage"]+" -C "+grabpath+" .","Couldn't create stage tarball",badval=2)

#vim: ts=4 sw=4 sta et sts=4 ai
