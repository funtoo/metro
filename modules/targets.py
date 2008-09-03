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
			raise CatalystError, "Total config errors: "+`failcount`+" - stopping."

	def require(self,mylist):
		missing=self.settings.missing(mylist)
		if missing:
			raise CatalystError,"Missing required configuration values "+`missing`

	def recommend(self,mylist):
		missing=self.settings.missing(mylist)
		for item in missing:
			print "Warning: recommended value \""+item+"\" not defined."

	def clear_dir(self,path):
	    if not os.path.isdir(path):
	    	return
		print "Emptying directory",path
		# stat the dir, delete the dir, recreate the dir and set the proper perms and ownership
		mystat=os.stat(path)
		if os.uname()[0] == "FreeBSD": # There's no easy way to change flags recursively in python
			os.system("chflags -R noschg "+path)
		shutil.rmtree(path)
		os.makedirs(path,0755)
		os.chown(path,mystat[ST_UID],mystat[ST_GID])
		os.chmod(path,mystat[ST_MODE])


	def bin(self,myc):
		"""look through the environmental path for an executable file named whatever myc is"""
		# this sucks. badly.
		p=self.env["PATH"]
		for x in p.split(":"):
			#if it exists, and is executable
			if os.path.exists("%s/%s" % (x,myc)) and os.stat("%s/%s" % (x,myc))[0] & 0x0248:
				return "%s/%s" % (x,myc)
		raise CatalystError, "Can't find command "+myc

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
					raise CatalystError,myexc
			else:
				if retval != 0:
					raise CatalystError,myexc
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

	def exec_in_chroot(self,key):

		if not self.settings.has_key(key):
			raise CatalystError, "exec_in_chroot: key \""+key+"\" not found."
	
		if type(self.settings[key]) != types.ListType:
			raise CatalystError, "exec_in_chroot: key \""+key+"\" is not a multi-line element."

		outfile = self.settings["chrootdir"]+"/tmp/"+key+".sh"
		outdir = os.path.dirname(outfile)

		if not os.path.exists(outdir):
			os.makedirs(outdir)
		outfd = open(outfile,"w")
		
		for x in self.settings[key]:
			outfd.write(x+"\n")

		outfd.close()

		if self.settings["arch"] == "x86" and os.uname[4] == "x86_64":
			cmds = [self.bin("linux32"),self.bin("chroot"),self.settings["chrootdir"],self.bin("bash")]
		else:
			cmds = [self.bin("chroot"),self.settings["chrootdir"],self.bin("bash")]

		cmds.append("/tmp/"+key+".sh")

		retval = spawn(cmds, env=self.env )

		if retval != 0:
			raise CatalystError, "Command failure: "+" ".join(cmds)

	def __init__(self,settings):
		target.__init__(self,settings)

		# DEFINE GENERAL LINUX CHROOT MOUNTS

		self.mounts=[ "/proc","/dev", "/dev/pts" ]
		self.mountmap={"/proc":"/proc", "/dev":"/dev", "/dev/pts":"/dev/pts"}

		# CCACHE SUPPORT FOR CHROOTS

		if self.settings.has_key("options") and "ccache" in self.settings["options"].split():
			if os.environ.has_key("CCACHE_DIR"):
				ccdir=os.environ["CCACHE_DIR"]
				del os.environ["CCACHE_DIR"]
			else:
				ccdir="/root/.ccache"
			if not os.path.isdir(ccdir):
					raise CatalystError, "Compiler cache support can't be enabled (can't find "+ccdir+")"
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
				raise CatalystError,"Couldn't bind mount "+src
			    
	
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
			raise CatalystError,"Couldn't umount one or more bind-mounts; aborting for safety."

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
						raise CatalystError, "Auto-unbind failed for "+x
					else:
						print "Auto-unbind successful..."
				except CatalystError:
					raise CatalystError, "Unable to auto-unbind "+x

class snapshot(target):
	def __init__(self,settings):
		target.__init__(self,settings)

		if os.path.exists("/etc/catalyst/snapshot.spec"):
			print "Reading in configuration from /etc/catalyst/snapshot.spec..."
			self.settings.collect("/etc/catalyst/snapshot.spec")

		self.require(["portname","portdir","version","target"])
		self.require(["storedir/snapshot"])

	def run(self):

		if os.path.exists(self.settings["workdir"]):
			print "Removing existing temporary work directory..."
			self.cmd( self.bin("rm") + " -rf " + self.settings["workdir"] )

		if "replace" in self.settings["options"].split():
			if os.path.exists(self.settings["storedir/snapshot"]):
				print "Removing existing snapshot..."
				self.cmd( self.bin("rm") + " -f " + self.settings["storedir/snapshot"])

		elif os.path.exists(self.settings["storedir/snapshot"]):
			print "Snapshot already exists at "+self.settings["storedir/snapshot"]+". Skipping..."
			return
		else:
			print self.settings["storedir/snapshot"],"does not exist - creating it..."
				
		# create required directories
		for dir in [ os.path.dirname(self.settings["storedir/snapshot"]), self.settings["workdir"]+"/portage" ]:
			if not os.path.exists(dir):
				os.makedirs(dir)
	
		# rsync options
		rsync_opts = "-a --delete --exclude /packages/ --exclude /distfiles/ --exclude /local/ --exclude CVS/ --exclude /.git/"
		rsync_cmd = self.bin("rsync") + " " + rsync_opts + " " + os.path.normpath(self.settings["portdir"])+"/ " + os.path.normpath(self.settings["workdir"]+"/portage")+"/"
		self.cmd(rsync_cmd,"Snapshot failure")
		tmpfile=os.path.dirname(self.settings["storedir/snapshot"])+"/."+os.path.basename(self.settings["storedir/snapshot"])
		
		self.cmd( self.bin("tar") + " -cjf " + tmpfile +" -C "+self.settings["workdir"]+" portage","Snapshot creation failure")
		self.cmd( self.bin("mv") + " " + tmpfile + " " + self.settings["storedir/snapshot"], "Couldn't move snapshot to final position" )

		# workdir cleanup is handled by catalyst calling our cleanup() method

class stage(chroot):

	def __init__(self,settings):
		chroot.__init__(self,settings)

		if os.path.exists("/etc/catalyst/stage.spec"):
			print "Reading in configuration from /etc/catalyst/stage.spec..."
			self.settings.collect("/etc/catalyst/stage.spec")

		# In the constructor, we want to define settings but not reference them if we can help it, certain things
		# like paths may not be able to be fully expanded yet until we define our goodies like "source", etc.

		self.require(["arch","subarch","profile","storedir/srcstage","storedir/deststage","storedir/snapshot","CHOST"])
		
		# look for user-specified USE, if none specified then fallback to HOSTUSE if specified
		if not self.settings.has_key("USE"):
			if self.settings.has_key("HOSTUSE"):
				self.settings["USE"]="$[HOSTUSE]"

		# If distdir, USE or CFLAGS not specified, alert the user that they might be missing them
		self.recommend(["distdir","USE","CFLAGS","MAKEOPTS"])

		# We also use an initial "~" as a trigger to build an unstable version of the portage tree. This
		# means we need to use ~arch rather than arch in ACCEPT_KEYWORDS. So if someone specified "~pentium4"
		# as subarch, we would set ACCEPT_KEYWORDS to "~x86" and later write this into make.conf.
		
		if self.settings["subarch"][0] == "~":
			self.settings["ACCEPT_KEYWORDS"] = "~"+self.settings["arch"]
		else:
			self.settings["ACCEPT_KEYWORDS"] = self.settings["arch"]

		# All the ~x86, ~pentium4, etc. unstable subarch build logic should be done now. Now we need to make
		# sure that we use the new variables for paths, below...

		if self.settings["hostarch"] == "amd64" and self.settings["arch"] == "x86":
			self.settings["chroot"]=self.bin("linux32")+" "+self.bin("chroot")
		else:
			self.settings["chroot"]=self.bin("chroot")

		# DEFINE GENTOO MOUNTS

		if self.settings.has_key("distdir"):
			self.mounts.append("/usr/portage/distfiles")
			self.mountmap["/usr/portage/distfiles"]=self.settings["distdir"]

		self.settings["chrootdir"]="$[workdir]/chroot"

	def run(self):

		if "replace" in self.settings["options"].split():
			if os.path.exists(settings["storedir/deststage"]):
				print "Removing existing stage..."
				self.cmd( self.bin("rm") + " -f " + self.settings["storedir/deststage"])
		# do not overwrite snapshot if it already exists
		elif os.path.exists(self.settings["storedir/deststage"]):
			print "Stage "+repr(self.settings["storedir/deststage"])+" already exists - skipping..."
			return
			#raise CatalystError,"Snapshot "+self.settings["storedir/snapshot"]+" already exists. Aborting."

		# look for required files
		for loc in [ "storedir/srcstage", "storedir/snapshot" ]:
			if not os.path.exists(self.settings[loc]):
				raise CatalystError,"Required file "+self.settings[loc]+" not found. Aborting."

		# BEFORE WE CLEAN UP - MAKE SURE WE ARE UNMOUNTED
		self.kill_chroot_pids()
		self.mount_safety_check()

		# BEFORE WE START - CLEAN UP ANY MESSES
		if os.path.exists(self.settings["workdir"]):
			print "Removing existing temporary work directory..."
			self.cmd( self.bin("rm") + " -rf " + self.settings["workdir"] )
		try:

			self.unpack()
			self.unpack_snapshot()

			# network config, etc.
			self.chroot_setup()

			self.bind()

			self.exec_in_chroot("chroot/prerun")
			self.exec_in_chroot("chroot/run")
			self.exec_in_chroot("chroot/postrun")
			
			self.unbind()
			
			# remove our tweaks...

			self.chroot_cleanup()

			# now let the spec-defined clean script do all the heavy lifting...

			self.exec_in_chroot("chroot/clean")
			
		except:
		
			self.kill_chroot_pids()
			self.mount_safety_check()
			raise

		# Now, grab the fruits of our labor.
		self.capture()

	def unpack(self):
		unpack_cmd=self.bin("tar")+" xjpf "+self.settings["storedir/srcstage"]+" -C "+self.settings["chrootdir"]
		
		self.mount_safety_check()
			
		if not os.path.exists(self.settings["chrootdir"]):
			os.makedirs(self.settings["chrootdir"])

		# Ensure /tmp exists in chroot - may not be required anymore
		if not os.path.exists(self.settings["chrootdir"]+"/tmp"):
			os.makedirs(self.settings["chrootdir"]+"/tmp",1777)
			
		self.cmd(unpack_cmd,"Error unpacking source stage.")

	def unpack_snapshot(self):
		destdir=os.path.normpath(self.settings["chrootdir"]+"/usr/portage")
		cleanup_errmsg="Error removing existing snapshot directory."
		cleanup_msg="Cleaning up existing portage tree (This can take a long time) ..."
		unpack_cmd="tar xjpf "+self.settings["storedir/snapshot"]+" -C "+self.settings["chrootdir"]+"/usr"
		unpack_errmsg="Error unpacking snapshot"
	
		if not os.path.exists(destdir):
			os.makedirs(destdir,0755)
		    	
		print "Unpacking \""+self.settings["storedir/snapshot"]+" ..."
		self.cmd(unpack_cmd,unpack_errmsg)

	def proxy_config(self):
		# SETUP PROXY SETTINGS - ENVSCRIPT DOESN'T ALWAYS WORK. THIS DOES.
		print "Writing out proxy settings..."
		try:
			a=open(self.settings["chrootdir"]+"/etc/env.d/99zzcatalyst","w")
		except:
			raise CatalystError,"Couldn't open "+self.settings["chrootdir"]+"/etc/env.d/99zzcatalyst for writing"
		for x in ["http_proxy","ftp_proxy","RSYNC_PROXY"]:
			if os.environ.has_key(x):
				a.write(x+"=\""+os.environ[x]+"\"\n")
			else:
				a.write("# "+x+" is not set")
		a.close()
	
	def locale_config(self):
		if self.settings.has_key("locales"):
			# our locale.gen template (nothing in it except comments: )
			srcfile=self.settings["sharedir"]+"/misc/locale.gen"
			# our destination locale.gen file:
			locfile=self.settings["chrootdir"]+"/etc/locale.gen"
			cmd("rm -f "+locfile)
			cmd("install -m0644 -o root -g root "+srcfile+" "+locfile)
			try:
				#open to append locale entries
				a=open(locfile,"a")
			except:
				raise CatalystError,"Couldn't open "+locfile+" for writing."
			for localepair in self.settings["locales"]:
				locale,charmap = localepair.split("/")
				a.write(locale+" "+charmap+"\n")
			#all done writing out our locales/charmaps
			a.close()

	def network_config(self):
		# Copy over /etc/resolv.conf and /etc/hosts from our root filesystem since we may need them for network connectivity.
		# Back up original files.
		for file in [ "/etc/resolv.conf", "/etc/hosts" ]:
			respath=self.settings["chrootdir"]+file
			if os.path.exists(file):
				if os.path.exists(respath):
					self.cmd("/bin/cp "+respath+" "+respath+".bck","Couldn't back up "+file)
				self.cmd("/bin/cp "+file+" "+respath,"Couldn't copy "+file+" into place.")

	def portage_config(self):
		self.cmd("/bin/rm -f "+self.settings["chrootdir"]+"/etc/make.conf","Could not remove "+self.settings["chrootdir"]+"/etc/make.conf")
		myf=open(self.settings["chrootdir"]+"/etc/make.conf","w")
		myf.write("# These settings were set by the catalyst build script that automatically\n# built this stage.\n")
		myf.write("# Please consult /etc/make.conf.example for a more detailed example.\n")
		for opt in ["CFLAGS","CXXFLAGS","LDFLAGS","CBUILD","CHOST","ACCEPT_KEYWORDS","USE"]:
			if self.settings.has_key(opt):
				myf.write(opt+'="'+self.settings[opt]+'"\n')
		myf.close()

	def chroot_setup(self):
		print "Setting up chroot..."
		self.proxy_config()
		self.locale_config()
		self.network_config()
		self.portage_config()
	
	def chroot_cleanup(self):

		# Philosophy: Catalyst should only do the bare minimum cleanup in Python. The bulk of the cleanup work should be defined in
		# the spec file so that it is not hard-coded into the Catalyst tool itself.

	    	# We only need to clean the following things if we were merging to our own filesystem: (ROOT=="/"). Otherwise cleanup is not
		# necessary as these changes won't get stuck inside our stage tarball.
		
		if self.settings["ROOT"]=="/":

			for x in ["/etc/profile.env","/etc/csh.env","/etc/env.d/99zzcatalyst"]:
				if os.path.exists(self.settings["chrootdir"]+x):
					print "Cleaning chroot: "+x+"... " 
					self.cmd("rm -f "+self.settings["chrootdir"]+x)

			for file in [ "/etc/resolv.conf", "/etc/hosts" ]:
				self.cmd("mv -f "+self.settings["chrootdir"]+file+".bck "+self.settings["chrootdir"]+file, "Couldn't restore "+file)

		# Run our "clean" bash script, which should do all of the heavy lifting...

	def capture(self):
		"""capture target in a tarball"""
		# IF TARGET EXISTS, REMOVE IT - WE WILL CREATE A NEW ONE
		if os.path.exists(self.settings["storedir/deststage"]):
			if os.path.isfile(self.settings["storedir/deststage"]):
				self.cmd("rm -f "+self.settings["storedir/deststage"], "Could not remove existing file: "+self.settings["storedir/deststage"])
			else:
				raise CatalystError,"Can't remove existing "+self.settings["storedir/deststage"]+" - not a file. Aborting."

		grabpath=os.path.normpath(self.settings["chrootdir"]+self.settings["ROOT"])
		
		# Ensure target stage directory exists (might be several subdirectories that need to be created)
		if not os.path.exists(os.path.dirname(self.settings["storedir/deststage"])):
			os.makedirs(os.path.dirname(self.settings["storedir/deststage"]))

		print "Creating stage tarball..."
		self.cmd("tar cjpf "+self.settings["storedir/deststage"]+" -C "+grabpath+" .","Couldn't create stage tarball",badval=2)

class stage3(stage):

	def __init__(self,settings):
		stage.__init__(self,settings)
		
		# set standard hard-coded variables for this stage
		self.settings["ROOT"]="/"
		self.settings["rootdir"] = self.settings["workdir"]
		self.settings["source"] = "stage2"

class stage2(stage):

	def __init__(self,settings):
		stage.__init__(self,settings)

		self.settings["ROOT"] = "/"
		self.settings["rootdir"] = self.settings["workdir"]
		self.settings["source"] = "stage1"

class stage1(stage):

	def __init__(self,settings):
		stage.__init__(self,settings)

		self.settings["ROOT"] = "/tmp/stage1root"
		self.settings["rootdir"] = self.settings["workdir"]+"/tmp/stage1root"
		self.settings["source"] = "stage3"
	
directory = { "stage1" : stage1, "stage2" : stage2, "stage3" : stage3 , "snapshot" : snapshot }

#vim: ts=4 sw=4 sta et sts=4 ai
