#!/usr/bin/python3

from subprocess import Popen
import os, sys, time

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

def spawn(cmd, env):
	print("Spawn: ",cmd,env)
	pid = Popen(cmd, env=env)
	exitcode = pid.wait()
	if exitcode != 0:
		print("Errors!")
		return exitcode
	return 0

class timestampFile(object):

	"Class to create timestamp files; used for tracking in-progress metro builds."

	def __init__(self,path):
		self.path = path
		self.created = False

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
				sys.stderr.write("# Removing stale timestamp: %s" % self.path)
				try:
					os.unlink(self.path)
				except FileNotFoundError:
					pass
		return exists

	def unlink(self):
		if self.created and os.path.exists(self.path):
			os.unlink(self.path)

	def create(self):
		if self.exists():
			return False
		try:
			out = open(self.path,"w")
		except IOError:
			return False
		out.write(str(os.getpid()))
		out.close()
		self.created = True
		return True

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

if __name__ == "__main__":
	a = timestampFile("/var/tmp/foo.ts")
	print(a.exists())
	print(a.create())
	print(a.get())
	print(a.age())

# vim: ts=4 sw=4 noet
