#!/usr/bin/python3

from subprocess import Popen
import os

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
