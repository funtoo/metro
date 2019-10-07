import os, sys, types
from glob import glob

from metro_support import MetroError

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

	def __init__(self, settings, cr):
		self.settings = settings
		# new CommandRunner (logger) object:
		self.cr = cr
		self.env = {}
		self.env["PATH"] = "/bin:/sbin:/usr/bin:/usr/sbin"
		if "TERM" in os.environ:
			self.env["TERM"] = os.environ["TERM"]
		self.required_files = []
		if not os.path.exists("/usr/bin/chroot"):
			self.cmds["chroot"] = "/usr/sbin/chroot"

	def run(self):
		self.check_required_files()
		self.clean_path(recreate=True)
		self.run_script("steps/run")
		self.clean_path()

	def run_script(self, key, chroot=None, optional=False, error_scan=False):
		if key not in self.settings:
			if optional:
				return
			raise MetroError("run_script: key '%s' not found." % (key,))

		if type(self.settings[key]) != list:
			raise MetroError("run_script: key '%s' is not a multi-line element." % (key, ))

		self.cr.mesg("run_script: running %s..." % key)

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
			if self.settings["target/arch_desc"] == "x86-32bit" and os.uname()[4] == "x86_64":
				cmds.append(self.cmds["linux32"])
			cmds.append(self.cmds["chroot"])
			cmds.append(chroot)
			cmds.append(chrootfile)
		else:
			cmds.append(outfile)

		retval = self.cr.run(cmds, env=self.env, error_scan=error_scan)
		if retval != 0:
			raise MetroError("Command failure (key %s, return value %s) : %s" % (key, repr(retval), " ".join(cmds)))

		# it could have been cleaned by our outscript, so if it exists:
		if os.path.exists(outfile):
			os.unlink(outfile)

	def check_required_files(self):
		for loc in self.required_files:
			try:
				matches = glob(self.settings[loc])
			except:
				raise MetroError("Setting %s is set to %s; glob failed." % (loc, repr(self.settings[loc])))
			if len(matches) == 0:
				loc_no_ending = None
				found = False
				# look for uncompressed version of file:
				for ending in [ ".tar.xz", ".tar.gz", "tar.bz2" ]:
					if self.settings[loc].endswith(ending):
						zap_part = "." + ending.split(".")[-1]
						# remove .gz, .xz extension:
						loc_no_ending = self.settings[loc][:-len(zap_part)]
						break
				if loc_no_ending is not None:
					matches = glob(loc_no_ending)
					if len(matches) != 0:
						print("Found uncompressed file: %s" % loc_no_ending)
						found = True
				if not found:
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
		self.cr.mesg("Executing \""+mycmd+"\"...")
		try:
			sys.stdout.flush()
			retval = self.cr.run(mycmd.split(), self.env)
			if badval:
				# This code is here because tar has a retval of 1 for non-fatal warnings
				if retval == badval:
					raise MetroError(myexc)
			else:
				if retval != 0:
					raise MetroError(myexc)
		except:
			raise

# vim: ts=4 sw=4 noet
