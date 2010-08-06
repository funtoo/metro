import os,string,imp,types,shutil
from catalyst_support import *
from stat import *
import os
from glob import glob

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

	def run(self):
		self.runScript("steps/run")
		if self.settings.has_key("trigger/ok/run"):
			self.runScript("trigger/ok/run")
		return

	def runScript(self,key,chroot=None):
		if not self.settings.has_key(key):
			raise MetroError, "runScript: key \""+key+"\" not found."
		if type(self.settings[key]) != types.ListType:
			raise MetroError, "runScript: key \""+key+"\" is not a multi-line element."
		print
		print "runScript: running %s..." % key
		print

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
			if self.settings["target/arch"] == "x86" and os.uname()[4] == "x86_64":
				cmds = [bin["linux32"],bin["chroot"]]
			else:
				cmds = [bin["chroot"]]
			cmds.append(chroot)
			cmds.append(chrootfile)
		else:
			cmds.append(outfile)

		retval = spawn(cmds, env=self.env )
		if retval != 0:
			raise MetroError, "Command failure (key %s, return value %s) : %s" % ( key, repr(retval), " ".join(cmds))
		# it could have been cleaned by our outscript, so if it exists:
		if os.path.exists(outfile):
			os.unlink(outfile)


	def targetExists(self,key):
		if self.settings.has_key("metro/options") and "replace" in self.settings["metro/options"].split():
			if os.path.exists(self.settings[key]):
				print "Removing existing file %s..." % self.settings[key]
				self.cmd( bin["rm"] + " -f " + self.settings[key])
			return False
		elif os.path.exists(self.settings[key]):
			print "File %s already exists - skipping..." % self.settings[key]
			return True
		else:
			return False

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
			# This line ensures that the root /var/tmp/metro path has proper 0700 perms:
			self.cmd(bin["install"]+" -d -m 0700 -g root -o root " + self.settings["path/tmp"])
			# This creates the directory we want.
			self.cmd(bin["install"]+" -d -m 0700 -g root -o root "+path)
			# The 0700 perms prevent Metro-generated /tmp directories from being abused by others -
			# because they are world-writeable, they could be used by malicious local users to
			# inject arbitrary data/executables into a Metro build.
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

	def get_chroot_pids(self):
		cdir=self.settings["path/work"]
		pids=[]
		for pid in os.listdir("/proc"):
			if not os.path.isdir("/proc/"+pid):
				continue
			try:
				mylink = os.readlink("/proc/"+pid+"/exe")
			except OSError:
				# not a pid directory
				continue
			if mylink[0:len(cdir)] == cdir:
				pids.append([pid,mylink])
		return pids

	def kill_chroot_pids(self):
		for pid,mylink in self.get_chroot_pids():
			print "Killing process "+pid+" ("+mylink+")"
			self.cmd(bin["kill"]+" -9 "+pid)

	def runScriptInChroot(self,key,chroot=None):
		if chroot == None:
			return self.runScript(key,chroot=self.settings["path/work"])
		else:
			return self.runScript(key,chroot=chroot)

	def __init__(self,settings):
		target.__init__(self,settings)

		# DEFINE GENERAL LINUX CHROOT MOUNTS

		self.mounts=[ "/proc" ]
		self.mountmap={"/proc":"/proc" }

		# CCACHE SUPPORT FOR CHROOTS

		if not self.settings.has_key("metro/class"):
			return

		skey="metro/options/"+self.settings["metro/class"]

		# enable ccache and pkgcache support - all we do in python is bind-mount the right directory to the right place.

		for key, name, dest in [
				[ "path/cache/compiler", "cache/compiler", "/var/tmp/cache/compiler" ] ,
				[ "path/cache/package", "cache/package", "/var/tmp/cache/package" ] ,
				[ "path/cache/probe", "probe", "/var/tmp/cache/probe" ] ]:
			if self.settings.has_key(skey) and name in self.settings[skey].split():
				if not self.settings.has_key(key):
					raise MetroError, "Required setting %s not found (for %s option support)" % ( key, name )
				if not os.path.exists(self.settings[key]):
					os.makedirs(self.settings[key])
				self.mounts.append(dest)
				self.mountmap[dest]=self.settings[key]

	def bind(self):
		""" Perform bind mounts """
		for x in self.mounts:
			if not os.path.exists(self.settings["path/work"]+x):
				os.makedirs(self.settings["path/work"]+x,0755)

			if not os.path.exists(self.mountmap[x]):
				os.makedirs(self.mountmap[x],0755)

			src=self.mountmap[x]
			print "Mounting %s to %s..." % (src, x)
			if os.system(bin["mount"]+" --bind "+src+" "+self.settings["path/work"]+x) != 0:
				self.unbind()
				raise MetroError,"Couldn't bind mount "+src

	def unbind(self,attempt=0):
		myprefix = self.settings["path/work"]
		mounts = self.getActiveMounts()
		while len(mounts) != 0:
			# now, go through our dictionary and try to unmound
			progress = 0
			mpos = 0
			while mpos < len(mounts):
				self.cmd("umount "+mounts[mpos],badval=10)
				if not ismount(mounts[mpos]):
					del mounts[mpos]
					progress += 1
				else:
					mpos += 1
			if progress == 0:
				break

		mounts = self.getActiveMounts()
		if len(mounts):
			if attempt >= 3:
				mstring=""
				for x in mounts():
					mstring += x+"\n"
				raise MetroError,"The following bind mounts could not be unmounted: \n"+mstring
			else:
				attempt += 1
				self.kill_chroot_pids()
				self.unbind(attempt=attempt)

	def getActiveMounts(self):
		# os.path.realpath should ensure that we are comparing the right thing, if something in the path
		# is a symlink - like /var/tmp -> /foo. Because /proc/mounts will store the resolved path (ie.
		# /foo/metro) not the regular one (ie. /var/tmp/metro)
		prefix=os.path.realpath(self.settings["path/work"])
		# this used to have a "os.popen("mount")" which is not as accurate as the kernel list /proc/mounts.
		# The "mount" command relies on /etc/mtab which is not necessarily correct.
		myf=open("/proc/mounts","r")
		mylines=myf.readlines()
		myf.close()
		outlist=[]
		for line in mylines:
			mypath = line.split()[1]
			if mypath[0:len(prefix)] == prefix:
				outlist.append(mypath)
		return outlist

	def checkMounts(self):
		mymounts = self.getActiveMounts()
		if len(mymounts) == 0:
			return
		else:
			self.unbind()

	def run(self):
		if self.targetExists("path/mirror/target"):
			if self.settings.has_key("trigger/ok/run"):
				self.runScript("trigger/ok/run")
			return

		# look for required files
		for loc in [ "path/mirror/source" ]:
			matches = glob(self.settings[loc])
			if len(matches) ==0:
				raise MetroError,"Required file "+self.settings[loc]+" not found. Aborting."
			elif len(matches) > 1:
				raise MetroError,"Multiple matches found for required file pattern defined in '%s'; Aborting." % loc

		# BEFORE WE CLEAN UP - MAKE SURE WE ARE UNMOUNTED
		self.kill_chroot_pids()
		self.checkMounts()

		# BEFORE WE START - CLEAN UP ANY MESSES
		self.cleanPath(recreate=True)
		try:
			self.checkMounts()
			self.runScript("steps/unpack")

			self.bind()

			if self.settings.has_key("steps/chroot/prerun"):
				self.runScriptInChroot("steps/chroot/prerun")
			self.runScriptInChroot("steps/chroot/run")
			if self.settings.has_key("steps/chroot/postrun"):
				self.runScriptInChroot("steps/chroot/postrun")

			self.unbind()
		except:
			self.kill_chroot_pids()
			self.checkMounts()
			raise

		self.runScript("steps/capture")
		if self.settings.has_key("trigger/ok/run"):
			self.runScript("trigger/ok/run")
		self.cleanPath()


class snapshot(target):
	def __init__(self,settings):
		target.__init__(self,settings)

	def run(self):
		if self.targetExists("path/mirror/snapshot"):
			if self.settings.has_key("trigger/ok/run"):
				self.runScript("trigger/ok/run")
			return

		self.cleanPath(recreate=True)
		if not self.settings.has_key("steps/run"):
			raise MetroError, "Required steps in steps/run not found."
		self.runScript("steps/run")
		if self.settings.has_key("trigger/ok/run"):
			self.runScript("trigger/ok/run")
		self.cleanPath()

class stage(chroot):

	def __init__(self,settings):
		chroot.__init__(self,settings)

		# DEFINE GENTOO MOUNTS
		if self.settings.has_key("path/distfiles"):
			self.mounts.append("/usr/portage/distfiles")
			self.mountmap["/usr/portage/distfiles"]=self.settings["path/distfiles"]

		if not self.settings.has_key("portage/devices"):
			# if device nodes aren't to be manually created, let's bind-mount our main system's device nodes in place
			if self.settings["portage/ROOT"] != "/":
				# this seems to be needed for libperl to build (x2p) during stage1 - so we'll mount it....
				self.mounts.append("/dev")
				self.mounts.append("/dev/pts")
				self.mountmap["/dev"] = "/dev"
				self.mountmap["/dev/pts"] = "/dev/pts"
	def run(self):
		if self.targetExists("path/mirror/target"):
			if self.settings.has_key("trigger/ok/run"):
				self.runScript("trigger/ok/run")
			return

		# look for required files
		for loc in [ "path/mirror/source", "path/mirror/snapshot" ]:
			matches = glob(self.settings[loc])
			if len(matches) == 0:
				raise MetroError,"Required file "+self.settings[loc]+" not found. Aborting."
			elif len(matches) > 1:
				raise MetroError,"Multiple matches found for required file pattern defined in '%s'; Aborting." % loc

		# BEFORE WE CLEAN UP - MAKE SURE WE ARE UNMOUNTED
		self.kill_chroot_pids()
		self.checkMounts()

		# BEFORE WE START - CLEAN UP ANY MESSES
		self.cleanPath(recreate=True)
		try:
			self.checkMounts()
			self.runScript("steps/unpack")
			if self.settings.has_key("steps/unpack/post"):
				self.runScript("steps/unpack/post")
			self.bind()

			if self.settings.has_key("steps/chroot/prerun"):
				self.runScriptInChroot("steps/chroot/prerun")
			self.runScriptInChroot("steps/chroot/run")
			self.runScriptInChroot("steps/chroot/postrun")
			self.unbind()
			self.runScriptInChroot("steps/chroot/clean")
			if self.settings.has_key("steps/chroot/test"):
				self.runScriptInChroot("steps/chroot/test")
			if self.settings.has_key("steps/chroot/postclean"):
				self.runScriptInChroot("steps/chroot/postclean")
		except:
			self.kill_chroot_pids()
			self.checkMounts()
			raise
		# The build completed successfully.
		# Capture the results of our efforts:
		self.runScript("steps/capture")
		if self.settings.has_key("trigger/ok/run"):
			self.runScript("trigger/ok/run")
		# Now, we want to delete our build directory...
		self.kill_chroot_pids()
		self.checkMounts()
		self.cleanPath()
		# Now, we want to clean up our build-related caches, if configured to do so:
		if self.settings.has_key("metro/options"):
			if "clean/auto" in self.settings["metro/options"].split():
				if self.settings.has_key("path/cache/build"):
					self.cleanPath(self.settings["path/cache/build"])

#vim: ts=4 sw=4 sta et sts=4 ai
