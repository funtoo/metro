import os, sys, types
from glob import glob

from catalyst_support import MetroError, spawn, spawn_bash

class BaseTarget:
	cmds = {
		"bash": "/bin/bash",
		"chroot": "/usr/bin/chroot",
		"install": "/usr/bin/install",
		"kill": "/bin/kill",
		"linux32": "/usr/bin/linux32",
		"mount": "/bin/mount",
		"rm": "/bin/rm",
	}

	def __init__(self, settings):
		self.settings = settings
		self.env = {}
		self.env["PATH"] = "/bin:/sbin:/usr/bin:/usr/sbin"
		self.required_files = []

	def run(self):
		self.check_required_files()
		self.clean_path(recreate=True)
		self.run_script("steps/run")
		self.clean_path()

	def run_script(self, key, chroot=None, optional=False):
		print("run_script")
		print("key: %s" % key)
		print("key in self.settings", key in self.settings)
		if key not in self.settings:
			if optional:
				return
			raise MetroError("run_script: key '%s' not found." % (key,))

		if type(self.settings[key]) != list:
			raise MetroError("run_script: key '%s' is not a multi-line element." % (key, ))

		print("run_script: running %s..." % key)

		os.environ["PATH"] = self.env["PATH"]

		if chroot:
			chrootfile = "/tmp/"+key+".metro"
			outfile = chroot+chrootfile
		else:
			outfile = self.settings["path/tmp"]+"/pid/"+repr(os.getpid())

		outdir = os.path.dirname(outfile)
		if not os.path.exists(outdir):
			os.makedirs(outdir)

		with open(outfile, "w") as outfd:
			outfd.write("\n".join(self.settings[key]) + "\n")

		os.chmod(outfile, 0o755)

		cmds = []
		if chroot:
			if self.settings["target/arch"] == "x86" and os.uname()[4] == "x86_64":
				cmds.append(self.cmds["linux32"])
			cmds.append(self.cmds["chroot"])
			cmds.append(chroot)
			cmds.append(chrootfile)
		else:
			cmds.append(outfile)

		retval = spawn(cmds, env=self.env)
		if retval != 0:
			raise MetroError("Command failure (key %s, return value %s) : %s" % (key, repr(retval), " ".join(cmds)))

		# it could have been cleaned by our outscript, so if it exists:
		if os.path.exists(outfile):
			os.unlink(outfile)

	def target_exists(self, key):
		if "metro/options" in self.settings and "replace" in self.settings["metro/options"].split():
			if os.path.exists(self.settings[key]):
				print("Removing existing file %s..." % self.settings[key])
				self.cmd(self.cmds["rm"] + " -f " + self.settings[key])
			return False
		elif os.path.exists(self.settings[key]):
			print("File %s already exists - skipping..." % self.settings[key])
			return True
		else:
			return False

	def check_required_files(self):
		for loc in self.required_files:
			try:
				matches = glob(self.settings[loc])
			except:
				raise MetroError("Setting %s is set to %s; glob failed." % (loc, repr(self.settings[loc])))
			if len(matches) == 0:
				raise MetroError("Required file "+self.settings[loc]+" not found. Aborting.")
			elif len(matches) > 1:
				raise MetroError("Multiple matches found for required file pattern defined in '%s'; Aborting." % loc)

	def clean_path(self, path=None, recreate=False):
		if path == None:
			path = self.settings["path/work"]
		if os.path.exists(path):
			print("Cleaning up %s..." % path)
		self.cmd(self.cmds["rm"]+" -rf "+path)
		if recreate:
			# This line ensures that the root /var/tmp/metro path has proper 0700 perms:
			self.cmd(self.cmds["install"]+" -d -m 0700 -g root -o root " + self.settings["path/tmp"])
			# This creates the directory we want.
			self.cmd(self.cmds["install"]+" -d -m 0700 -g root -o root "+path)
			# The 0700 perms prevent Metro-generated /tmp directories from being abused by others -
			# because they are world-writeable, they could be used by malicious local users to
			# inject arbitrary data/executables into a Metro build.

	def cmd(self, mycmd, myexc="", badval=None):
		print("Executing \""+mycmd+"\"...")
		try:
			sys.stdout.flush()
			retval = spawn_bash(mycmd, self.env)
			if badval:
				# This code is here because tar has a retval of 1 for non-fatal warnings
				if retval == badval:
					raise MetroError(myexc)
			else:
				if retval != 0:
					raise MetroError(myexc)
		except:
			raise

# vim: ts=4 sw=4 et
