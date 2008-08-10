#!/usr/bin/python
import os
import fcntl
import errno
import sys
import string
import time
from catalyst_support import *

def writemsg(mystr):
	sys.stderr.write(mystr)
	sys.stderr.flush()

class LockDir:
	locking_method=fcntl.flock
	lock_dirs_in_use=[]
	die_on_faile_lock=True
	def __del__(self):
		self.clean_my_hardlocks()
		self.delete_lock_from_path_list()
		if self.islocked():
			self.fcntl_unlock()
	def __init__(self,lockdir):
		self.locked=False
		self.myfd=None
		self.set_gid(250)
		self.locking_method=LockDir.locking_method
		self.set_lockdir(lockdir)
		self.set_lockfilename(".catalyst_lock")
		self.set_lockfile()
	
		if LockDir.lock_dirs_in_use.count(lockdir)>0:
			raise "This directory already associated with a lock object"
		else:
			LockDir.lock_dirs_in_use.append(lockdir)
	
		self.hardlock_paths={}
	


	def delete_lock_from_path_list(self):
		i=0
		try:
			if LockDir.lock_dirs_in_use:
				for x in LockDir.lock_dirs_in_use:
					if LockDir.lock_dirs_in_use[i] == self.lockdir:
						del LockDir.lock_dirs_in_use[i]
						break
						i=i+1
		except AttributeError:
			pass

	def islocked(self):
		if self.locked:
			return True
		else:
			return False

	def set_gid(self,gid):
		if not self.islocked():
			#print "setting gid to", gid 
			self.gid=gid

	def set_lockdir(self,lockdir):
		if not os.path.exists(lockdir):
			os.makedirs(lockdir)
		if os.path.isdir(lockdir):
			if not self.islocked():
				if lockdir[-1] == "/":
					lockdir=lockdir[:-1]
				self.lockdir=normpath(lockdir)
				#print "setting lockdir to", self.lockdir
		else:
			raise "the lock object needs a path to a dir"

	def set_lockfilename(self,lockfilename):
		if not self.islocked():
			self.lockfilename=lockfilename
			#print "setting lockfilename to", self.lockfilename
	
	def set_lockfile(self):
		if not self.islocked():
			self.lockfile=normpath(self.lockdir+'/'+self.lockfilename)
			#print "setting lockfile to", self.lockfile
    
	def read_lock(self):
		if not self.locking_method == "HARDLOCK":
			self.fcntl_lock("read")
		else:
			print "HARDLOCKING doesnt support shared-read locks"
			print "using exclusive write locks"
			self.hard_lock()
    
	def write_lock(self):
		if not self.locking_method == "HARDLOCK":
			self.fcntl_lock("write")
		else:
			self.hard_lock()

	def unlock(self):
		if not self.locking_method == "HARDLOCK":
			self.fcntl_unlock()
		else:
			self.hard_unlock()

	def fcntl_lock(self,locktype):
		if self.myfd==None:
			if not os.path.exists(os.path.dirname(self.lockdir)):
				raise DirectoryNotFound, os.path.dirname(self.lockdir)
			if not os.path.exists(self.lockfile):
				old_mask=os.umask(000)
				self.myfd = os.open(self.lockfile, os.O_CREAT|os.O_RDWR,0660)
				try:
					if os.stat(self.lockfile).st_gid != self.gid:
						os.chown(self.lockfile,os.getuid(),self.gid)
				except SystemExit, e:
					raise
				except OSError, e:
					if e[0] == 2: #XXX: No such file or directory
						return self.fcntl_locking(locktype)
					else:
						writemsg("Cannot chown a lockfile. This could cause inconvenience later.\n")

				os.umask(old_mask)
			else:
				self.myfd = os.open(self.lockfile, os.O_CREAT|os.O_RDWR,0660)
	
		try:
			if locktype == "read":
				self.locking_method(self.myfd,fcntl.LOCK_SH|fcntl.LOCK_NB)
			else:
				self.locking_method(self.myfd,fcntl.LOCK_EX|fcntl.LOCK_NB)
		except IOError, e:
			if "errno" not in dir(e):
				raise
			if e.errno == errno.EAGAIN:
				if not LockDir.die_on_failed_lock:
					# resource temp unavailable; eg, someone beat us to the lock.
					writemsg("waiting for lock on %s\n" % self.lockfile)

					# try for the exclusive or shared lock again.
					if locktype == "read":
						self.locking_method(self.myfd,fcntl.LOCK_SH)
					else:
						self.locking_method(self.myfd,fcntl.LOCK_EX)
				else:
					raise LockInUse,self.lockfile
			elif e.errno == errno.ENOLCK:
				pass
			else:
				raise
		if not os.path.exists(self.lockfile):
			os.close(self.myfd)
			self.myfd=None
			#writemsg("lockfile recurse\n")
			self.fcntl_lock(locktype)
		else:
			self.locked=True
			#writemsg("Lockfile obtained\n")
	    
			    
	def fcntl_unlock(self):
		import fcntl
		unlinkfile = 1
		if not os.path.exists(self.lockfile):
			print "lockfile does not exist '%s'" % self.lockfile
			if (self.myfd != None):
				try:
					os.close(myfd)
					self.myfd=None
				except:
					pass
				return False

			try:
				if self.myfd == None:
					self.myfd = os.open(self.lockfile, os.O_WRONLY,0660)
					unlinkfile = 1
					self.locking_method(self.myfd,fcntl.LOCK_UN)
			except SystemExit, e:
				raise
			except Exception, e:
				os.close(self.myfd)
				self.myfd=None
				raise IOError, "Failed to unlock file '%s'\n" % self.lockfile
				try:
					# This sleep call was added to allow other processes that are
					# waiting for a lock to be able to grab it before it is deleted.
					# lockfile() already accounts for this situation, however, and
					# the sleep here adds more time than is saved overall, so am
					# commenting until it is proved necessary.
					#time.sleep(0.0001)
					if unlinkfile:
						InUse=False
						try:
							self.locking_method(self.myfd,fcntl.LOCK_EX|fcntl.LOCK_NB)
						except:
							print "Read lock may be in effect. skipping lockfile delete..."
							InUse=True
							### We won the lock, so there isn't competition for it.
							### We can safely delete the file.
							###writemsg("Got the lockfile...\n")
							###writemsg("Unlinking...\n")
							self.locking_method(self.myfd,fcntl.LOCK_UN)
					if not InUse:
						os.unlink(self.lockfile)
						os.close(self.myfd)
						self.myfd=None
						#print "Unlinked lockfile..."
				except SystemExit, e:
					raise
				except Exception, e:
					# We really don't care... Someone else has the lock.
					# So it is their problem now.
					print "Failed to get lock... someone took it."
					print str(e)

					# why test lockfilename?  because we may have been handed an
					# fd originally, and the caller might not like having their
					# open fd closed automatically on them.
					#if type(lockfilename) == types.StringType:
					#        os.close(myfd)
	
		if (self.myfd != None):
			os.close(self.myfd)
			self.myfd=None
			self.locked=False
			time.sleep(.0001)

	def hard_lock(self,max_wait=14400):
		"""Does the NFS, hardlink shuffle to ensure locking on the disk.
		We create a PRIVATE lockfile, that is just a placeholder on the disk.
		Then we HARDLINK the real lockfile to that private file.
		If our file can 2 references, then we have the lock. :)
		Otherwise we lather, rise, and repeat.
		We default to a 4 hour timeout.
		"""

		self.myhardlock = self.hardlock_name(self.lockdir)

		start_time = time.time()
		reported_waiting = False

		while(time.time() < (start_time + max_wait)):
			# We only need it to exist.
			self.myfd = os.open(self.myhardlock, os.O_CREAT|os.O_RDWR,0660)
			os.close(self.myfd)

			self.add_hardlock_file_to_cleanup()
			if not os.path.exists(self.myhardlock):
				raise FileNotFound, "Created lockfile is missing: %(filename)s" % {"filename":self.myhardlock}
			try:
				res = os.link(self.myhardlock, self.lockfile)
			except SystemExit, e:
				raise
			except Exception, e:
				#print "lockfile(): Hardlink: Link failed."
				#print "Exception: ",e
				pass

			if self.hardlink_is_mine(self.myhardlock, self.lockfile):
				# We have the lock.
				if reported_waiting:
					print
				return True

			if reported_waiting:
				writemsg(".")
			else:
				reported_waiting = True
				print
				print "Waiting on (hardlink) lockfile: (one '.' per 3 seconds)"
				print "Lockfile: " + self.lockfile
			time.sleep(3)

		os.unlink(self.myhardlock)
		return False

	def hard_unlock(self):
		try:
			if os.path.exists(self.myhardlock):
				os.unlink(self.myhardlock)
			if os.path.exists(self.lockfile):
				os.unlink(self.lockfile)
		except SystemExit, e:
			raise
		except:
			writemsg("Something strange happened to our hardlink locks.\n")

	def add_hardlock_file_to_cleanup(self):
		#mypath = self.normpath(path)
		if os.path.isdir(self.lockdir) and os.path.isfile(self.myhardlock):
			self.hardlock_paths[self.lockdir]=self.myhardlock
    
	def remove_hardlock_file_from_cleanup(self):
		if self.hardlock_paths.has_key(self.lockdir):
			del self.hardlock_paths[self.lockdir]
			print self.hardlock_paths

	def hardlock_name(self, path):
		mypath=path+"/.hardlock-"+os.uname()[1]+"-"+str(os.getpid())
		newpath = os.path.normpath(mypath)
		if len(newpath) > 1:
			if newpath[1] == "/":
				newpath = "/"+newpath.lstrip("/")
		return newpath


	def hardlink_is_mine(self,link,lock):
		import stat
		try:
			myhls = os.stat(link)
			mylfs = os.stat(lock)
		except SystemExit, e:
			raise
		except:
			myhls = None
			mylfs = None

		if myhls:
			if myhls[stat.ST_NLINK] == 2:
				return True
		if mylfs:
			if mylfs[stat.ST_INO] == myhls[stat.ST_INO]:
				return True
		return False

	def hardlink_active(lock):
		if not os.path.exists(lock):
			return False

	def clean_my_hardlocks(self):
		try:
			for x in self.hardlock_paths.keys():
				self.hardlock_cleanup(x)
		except AttributeError:
			pass

	def hardlock_cleanup(self,path):
		mypid  = str(os.getpid())
		myhost = os.uname()[1]
		mydl = os.listdir(path)
		results = []
		mycount = 0

		mylist = {}
		for x in mydl:
			filepath=path+"/"+x
			if os.path.isfile(filepath):
				parts = filepath.split(".hardlock-")
			if len(parts) == 2:
				filename = parts[0]
				hostpid  = parts[1].split("-")
				host  = "-".join(hostpid[:-1])
				pid   = hostpid[-1]
			if not mylist.has_key(filename):
				mylist[filename] = {}
			    
			if not mylist[filename].has_key(host):
				mylist[filename][host] = []
				mylist[filename][host].append(pid)
				mycount += 1
			else:
				mylist[filename][host].append(pid)
				mycount += 1


		results.append("Found %(count)s locks" % {"count":mycount})
		for x in mylist.keys():
			if mylist[x].has_key(myhost):
				mylockname = self.hardlock_name(x)
				if self.hardlink_is_mine(mylockname, self.lockfile) or \
					not os.path.exists(self.lockfile):
					for y in mylist[x].keys():
						for z in mylist[x][y]:
							filename = x+".hardlock-"+y+"-"+z
							if filename == mylockname:
								self.hard_unlock()
								continue
							try:
								# We're sweeping through, unlinking everyone's locks.
								os.unlink(filename)
								results.append("Unlinked: " + filename)
							except SystemExit, e:
								raise
							except Exception,e:
								pass
					try:
						os.unlink(x)
						results.append("Unlinked: " + x)
						os.unlink(mylockname)
						results.append("Unlinked: " + mylockname)
					except SystemExit, e:
						raise
					except Exception,e:
						pass
				else:
					try:
						os.unlink(mylockname)
						results.append("Unlinked: " + mylockname)
					except SystemExit, e:
						raise
					except Exception,e:
						pass
		return results


if __name__ == "__main__":

	def lock_work():
		print 
		for i in range(1,6):
			print i,time.time()
			time.sleep(1)
		print
	def normpath(mypath):
		newpath = os.path.normpath(mypath)
		if len(newpath) > 1:
			if newpath[1] == "/":
				newpath = "/"+newpath.lstrip("/")
		return newpath

	print "Lock 5 starting"
	import time
	Lock1=LockDir("/tmp/lock_path")
	Lock1.write_lock() 
	print "Lock1 write lock"
	
	lock_work()
	
	Lock1.unlock() 
	print "Lock1 unlock"
	
	Lock1.read_lock()
	print "Lock1 read lock"
	
	lock_work()
	
	Lock1.unlock() 
	print "Lock1 unlock"

	Lock1.read_lock()
	print "Lock1 read lock"
	
	Lock1.write_lock()
	print "Lock1 write lock"
	
	lock_work()
	
	Lock1.unlock()
	print "Lock1 unlock"
	
	Lock1.read_lock()
	print "Lock1 read lock"
	
	lock_work()
	
	Lock1.unlock()
	print "Lock1 unlock"
#Lock1.write_lock()
#time.sleep(2)
#Lock1.unlock()
    ##Lock1.write_lock()
    #time.sleep(2)
    #Lock1.unlock()
