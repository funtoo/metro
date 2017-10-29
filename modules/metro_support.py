#!/usr/bin/python3

import os, sys, subprocess, time, pwd, grp
from importlib import import_module
import json

def ismount(path):
	"enhanced to handle bind mounts"
	if os.path.ismount(path):
		return 1
	a=os.popen("mount")
	mylines=a.readlines()
	a.close()
	for line in mylines:
		mysplit=line.split()
		if os.path.normpath(path) == os.path.normpath(mysplit[2]):
			return 1
	return 0

class MetroError(Exception):
	def __init__(self, *args):
		self.args = args
	def __str__(self):
		if len(self.args) == 1:
			return str(self.args[0])
		else:
			return "(no message)"

class MetroSetup(object):

	def __init__(self, verbose=False, debug=False):

		self.debug = debug
		self.verbose = verbose

		self.flexdata = import_module("flexdata")
		self.targets = import_module("targets")

	def getSettings(self, args={}, extraargs=None):

		self.configfile = os.path.expanduser("~/.metro")
		# config settings setup

		if self.verbose:
			print("Using main configuration file %s.\n" % self.configfile)
		settings = self.flexdata.collection(self.debug)

		if os.path.exists(self.configfile):
			settings.collect(self.configfile, None)
			settings["path/config"] = os.path.dirname(self.configfile)
		else:
			raise RuntimeError("config file '%s' not found\nPlease copy %s to ~/.metro and customize for your environment." %
				(self.configfile, (os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + "/metro.conf")))

		for key, value in list(args.items()):
			if key[-1] == ":":
				settings[key[:-1]] = value
			else:
				raise RuntimeError("cmdline argument '%s' invalid - does not end in a colon" % key)

		# add extra values
		if extraargs:
			for arg in list(extraargs.keys()):
				settings[arg] = extraargs[arg]
		settings.runCollector()
		if settings["portage/MAKEOPTS"] == "auto":
			settings["portage/MAKEOPTS"] = "-j%s" % (int(subprocess.getoutput("nproc --all")) + 1)

		return settings

class CommandRunner(object):

	"CommandRunner is a class that allows commands to run, and messages to be displayed. By default, output will go to a log file. Messages will appear on stdout and in the logs."

	def __init__(self, settings=None, logging=True):
		self.settings = settings
		self.logging = logging
		if self.settings and self.logging:
			self.fname = self.settings["path/mirror/target/path"] + "/log/" + self.settings["target"] + ".txt"
			if not os.path.exists(os.path.dirname(self.fname)):
				# create output directory for logs
				self.logging = False
				self.run(["install", "-o", self.settings["path/mirror/owner"], "-g", self.settings["path/mirror/group"], "-m", self.settings["path/mirror/dirmode"], "-d", os.path.dirname(self.fname)], {})
				self.logging = True
			self.cmdout = open(self.fname,"w+")
			# set logfile ownership:
			os.chown(self.fname, pwd.getpwnam(self.settings["path/mirror/owner"]).pw_uid, grp.getgrnam(self.settings["path/mirror/group"]).gr_gid)
			sys.stdout.write("Logging output to %s.\n" % self.fname)

	def mesg(self, msg):
		if self.logging:
			self.cmdout.write(msg + "\n")
			self.cmdout.flush()
		sys.stdout.write(msg + "\n")

	def run(self, cmdargs, env, error_scan=False):
		self.mesg("Running command: %s (env %s) " % ( cmdargs,env ))
		try:
			if self.logging:
				cmd = subprocess.Popen(cmdargs, env=env, stdout=self.cmdout, stderr=subprocess.STDOUT)
			else:
				cmd = subprocess.Popen(cmdargs, env=env)
			exitcode = cmd.wait()
		except KeyboardInterrupt:
			cmd.terminate()
			self.mesg("Interrupted via keyboard!")
			raise
		else:
			if exitcode != 0:
				self.mesg("Command exited with return code %s" % exitcode)
				if error_scan and self.logging:
					# scan log for errors -- and extract them!
					self.mesg("Attempting to extract failed ebuild information...")
					if self.cmdout:
						self.cmdout.flush()
					s, out = subprocess.getstatusoutput('cat %s | grep "^ \* ERROR: " | sort -u | sed -e \'s/^ \\* ERROR: \\(.*\\) failed (\\(.*\\) phase).*/\\1 \\2/g\'' % self.fname)
					if s == 0:
						errors = []
						for line in out.split('\n'):
							print("Processing line",line)
							parts = line.split()
							if len(parts) != 2:
								# not what we're looking for
								continue
							if len(parts[0].split("/")) != 2:
								continue
							errors.append({"ebuild" : parts[0], "phase" : parts[1]})
						if len(errors):
							fname = self.settings["path/mirror/target/path"] + "/log/errors.json"
							self.mesg("Detected failed ebuilds... writing to %s." % fname)
							a = open(fname,"w")
							a.write(json.dumps(errors, indent=4))
							a.close()
				return exitcode
			return 0

class stampFile(object):

	def __init__(self,path):
		self.path = path

	def getFileContents(self):
		return "replaceme"

	def exists(self):
		return os.path.exists(self.path)

	def get(self):
		if not os.path.exists(self.path):
			return False
		try:
			inf = open(self.path,"r")
		except IOError:
			return False
		data = inf.read()
		inf.close()
		try:
			return int(data) 
		except ValueError:
			return False

	def unlink(self):
		if os.path.exists(self.path):
			os.unlink(self.path)

	def wait(self,seconds):
		elapsed = 0
		while os.path.exists(self.path) and elapsed < seconds:
			sys.stderr.write(".")
			sys.stderr.flush()
			time.sleep(5)
			elapsed += 5
		if os.path.exists(self.path):
			return False
		return True

class fakeLockFile(stampFile):

	def __init__(self,path):
		stampFile.__init__(self,path)
		self.created = False

	def unlink(self):
		pass

	def create(self):
		self.created = True

	def exists(self):
		return False

	def unlink(self):
		pass

	def getFileContents(self):
		return ""

class lockFile(fakeLockFile):

	"Class to create lock files; used for tracking in-progress metro builds."

	def unlink(self):
		"only unlink if *we* created the file. Otherwise leave alone."
		if self.created and os.path.exists(self.path):
			os.unlink(self.path)

	def create(self):
		if self.exists():
			return False
		try:
			out = open(self.path,"w")
		except IOError:
			return False
		out.write(self.getFileContents())
		out.close()
		self.created = True
		return True

	def exists(self):
		exists = False
		if os.path.exists(self.path):
			exists = True
			mypid = self.get()
			if mypid == False:
				try:
					os.unlink(self.path)
				except FileNotFoundError:
					pass
				return False
			try:
				os.kill(mypid, 0)
			except OSError:
				exists = False
				# stale pid, remove:
				sys.stderr.write("# Removing stale lock file: %s\n" % self.path)
				try:
					os.unlink(self.path)
				except FileNotFoundError:
					pass
		return exists

	def unlink(self):
		if self.created and os.path.exists(self.path):
			os.unlink(self.path)

	def getFileContents(self):
		return(str(os.getpid()))


class countFile(stampFile):

	"Class to record fail count for builds."

	@property
	def count(self):
		try:
			f = open(self.path,"r")
			d = f.readlines()
			return int(d[0])
		except (IOError, ValueError):
			return None

	def increment(self):
		try:
			count = self.count
			if count == None:
				count = 0
			count += 1
			f = open(self.path,"w")
			f.write(str(count))
			f.close()
		except (IOError, ValueError):
			return None

if __name__ == "__main__":
	pass
# vim: ts=4 sw=4 noet
