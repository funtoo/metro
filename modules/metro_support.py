#!/usr/bin/python3

from subprocess import Popen
import os
from datetime import datetime

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

	format = "%Y-%m-%dT%H:%M:%S.%f"

	def __init__(self,path):
		self.path = path
		self.created = False

	def exists(self):
		return os.path.exists(self.path)

	def unlink(self):
		if self.created and os.path.exists(self.path):
			os.unlink(self.path)

	def create(self):
		if self.exists():
			return False
		now = datetime.utcnow()
		try:
			out = open(self.path,"w")
		except IOError:
			return False
		out.write(now.isoformat())
		out.close()
		self.created = True
		return True

	def get(self):
		if not self.exists():
			return False
		try:
			inf = open(self.path,"r")
		except IOError:
			return False
		data = inf.read()
		inf.close()
		dt = datetime.strptime(data,self.format)
		return dt

	def age(self):
		dt = self.get()
		if dt == False:
			return False
		return datetime.utcnow() - dt

if __name__ == "__main__":
	a = timestampFile("/var/tmp/foo.ts")
	print(a.exists())
	print(a.create())
	print(a.get())
	print(a.age())

