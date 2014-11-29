#!/usr/bin/python3

import os, sys, subprocess, time

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

def spawn(cmdargs, env, fname=None, tee=False, append=False):
	"""Run command cmd, with environment variables env.
		if fname != None, then it contains a filename to write output to.
		if tee == False (default), no command output will appear on stdout.
		if tee == True, then command output will also appear on stdout.
		(In both cases above, stderr is redirected to stdout).

		If append == False, then output file fname will be overwritten if it exists.
		If append == True, then output file fname will be appended to if it exists.
	"""
	fout = None
	if fname != None:
		if append:
			fout = open(fname,"ab")
		else:
			fout = open(fname,"rb")
		if tee:
			cmdout = subprocess.PIPE
		else:
			cmdout = fout
	else:
		cmdout = subprocess.STDOUT
		tee = False
	print("Running command: %s (env %s) " % ( cmdargs,env ))
	try:
		cmd = subprocess.Popen(cmdargs, env=env, stdout=cmdout, stderr=subprocess.STDOUT)
		if tee:
			if append:
				teecmdargs = ['tee', '-a', fname]
			else:
				teecmdargs = ['tee', fname]
			teecmd = subprocess.Popen(teecmdargs, stdin=cmd.stdout)
			cmd.stdout.close()
			exitcode = cmd.wait()
		else:
			exitcode = cmd.wait()
	except KeyboardInterrupt:
		cmd.terminate()
		if tee:
			teecmd.terminate()
		print("Interrupted!")
		return 1
	else:
		if exitcode != 0:
			print("Command exited with return code %s" % exitcode)
			return exitcode
		return 0
	finally:
		if fname and fout:
			fout.close()

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

class lockFile(stampFile):

	"Class to create lock files; used for tracking in-progress metro builds."

	def __init__(self,path):
		stampFile.__init__(self,path)
		self.created = False

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
	spawn(["/tmp/test.sh"],os.environ, "/tmp/foo.out",tee=True)
# vim: ts=4 sw=4 noet
