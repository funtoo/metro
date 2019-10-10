#!/usr/bin/python3

import os, sys
import time
from metro_support import MetroError, ismount
import subprocess

from .base import BaseTarget
from qemu import native_support, qemu_arch_settings

class ChrootTarget(BaseTarget):
	def __init__(self, settings, cr):
		BaseTarget.__init__(self, settings, cr)

		# we need a source archive
		self.required_files.append("path/mirror/source")

		# define general linux mount points
		self.mounts = { }

		options = ["cache/package"]

		# define various mount points for our cache support (ccache, binpkgs,
		# genkernel, etc).
		caches = [
			[ "path/cache/package", "cache/package", "/var/tmp/cache/package" ] ,
			[ "path/cache/kernel", "cache/kernel", "/var/tmp/cache/kernel" ] ,
			[ "path/cache/probe", "probe", "/var/tmp/cache/probe" ],
		]

		for key, name, dst in caches:
			if name in options:
				if key not in self.settings:
					raise MetroError("Required setting %s not found (for %s option support)" % (key, name))
				if self.settings[key] is not None:
					# package cache dir will not be defined for snapshot...
					self.cr.mesg("Enabling cache: %s" % key)
					self.mounts[dst] = self.settings[key]

	def run(self):
		self.check_required_files()

		# before we clean up - make sure we are unmounted
		self.kill_chroot_pids()
		self.unbind()

		# before we start - clean up any messes
		self.clean_path(recreate=True)

		try:
			self.run_script("steps/unpack")
			self.run_script("steps/unpack/post", optional=True)

			if "host/arch_desc" in self.settings:
				host_arch = self.settings["host/arch_desc"]
			else:
				uname_arch = os.uname()[4]
				if uname_arch in [ "x86_64", "AMD64" ]:
					host_arch = "x86-64bit"
				elif uname_arch in [ "x86", "i686", "i386"]:
					host_arch = "x86-32bit"
				else:
					raise MetroError("Unrecognized host architecture. Please set host/arch to x86-64bit, arm-32bit, etc. in ~/.metro.")

			if host_arch not in native_support.keys():
				raise MetroError("Arch specified in host/arch_desc \"%s\" not supported." % host_arch)
			target_arch = self.settings["target/arch_desc"]

			self.franken_chroot = False

			if host_arch != target_arch:
				if target_arch not in native_support[host_arch]:
					self.franken_chroot = True

			# FRANKEN-CHROOT SETUP

			found_chroot_bin = None

			if self.franken_chroot:
				for fchroot_bin in [ "/root/fchroot/bin/fchroot-simple", "/usr/bin/fchroot-simple" ]:
					if os.path.exists(fchroot_bin):
						found_chroot_bin = self.cmds["chroot"] = fchroot_bin
					break
				if found_chroot_bin is None:
					raise MetroError("Please install fchroot to /usr/bin or clone fchroot git repo to /root for non-native binary support.")

			# END FRANKEN-CHROOT SETUP

			self.bind()

			self.run_script_in_chroot("steps/chroot/prerun", optional=True)
			self.run_script_in_chroot("steps/chroot/run", error_scan=True)
			# capture info about built stage, prior to cleaning. Two part-process,
			# one part in chroot, and the other part outside the chroot.
			if self.settings["release/type"] == "official":
				self.run_script_in_chroot("steps/chroot/grabinfo", optional=True)
				self.run_script("steps/precapture", optional=True)
			# postrun is for cleaning with bind-mounts still active:
			self.run_script_in_chroot("steps/chroot/postrun", optional=True)
			self.unbind()
			self.run_script_in_chroot("steps/chroot/clean", optional=True)
			# re-add bind mounts -- only for tests to run...
			self.bind()
			self.run_script_in_chroot("steps/chroot/test", optional=True)
			self.unbind()
			self.run_script_in_chroot("steps/chroot/postclean", optional=True)
		except:
			self.kill_chroot_pids()
			self.unbind()
			raise
		self.run_script("steps/clean", optional=True)
		if self.settings["release/type"] == "official":
			self.run_script("steps/capture")
			self.run_script("trigger/ok/run", optional=True)

		self.kill_chroot_pids()
		self.unbind()
		self.clean_path()

	def get_chroot_pids(self):
		cdir = self.settings["path/cache/build"]
		pids = []
		for pid in os.listdir("/proc"):
			if not os.path.isdir("/proc/"+pid):
				continue
			try:
				mylink = os.readlink("/proc/"+pid+"/exe")
			except OSError:
				# not a pid directory
				continue
			if mylink[0:len(cdir)] == cdir:
				pids.append([pid, mylink])
		return pids

	def kill_chroot_pids(self):
		for pid, mylink in self.get_chroot_pids():
			print("Killing process "+pid+" ("+mylink+")")
			self.cmd(self.cmds["kill"]+" -9 "+pid)

	def run_script_in_chroot(self, key, optional=False, error_scan=False):
		return self.run_script(key, chroot=self.settings["path/work"], optional=optional, error_scan=error_scan)

	def bind(self):
		""" Perform bind mounts """
		self.cr.mesg("Mounting /proc in chroot...")
		os.system(self.cmds["mount"]+" none -t proc %s/proc" % self.settings["path/work"])
		self.cr.mesg("Mounting /dev in chroot...")
		os.system(self.cmds["mount"]+" --rbind /dev %s/dev" % self.settings["path/work"])
		for dst, src in list(self.mounts.items()):
			if not os.path.exists(src):
				os.makedirs(src, 0o755)

			wdst = self.settings["path/work"]+dst
			if not os.path.exists(wdst):
				os.makedirs(wdst, 0o755)

			self.cr.mesg("Mounting %s to %s ..." % (src, dst))
			if os.system(self.cmds["mount"]+" -R "+src+" "+wdst) != 0:
				self.unbind()
				raise MetroError("Couldn't bind mount "+src)
		self.mounts["/proc"] = "/proc"

	def unbind(self, attempt=0):
		mounts = self.get_active_mounts()
		while len(mounts) != 0:
			# now, go through our dictionary and try to unmount
			progress = 0
			mpos = 0
			while mpos < len(mounts):
				time.sleep(0.1)
				self.cmd("umount -Rl "+mounts[mpos], badval=10)
				if not ismount(mounts[mpos]):
					del mounts[mpos]
					progress += 1
				else:
					mpos += 1
			if progress == 0:
				break

		mounts = self.get_active_mounts()
		if len(mounts):
			if attempt >= 20:
				mstring = ""
				for mount in mounts:
					mstring += mount+"\n"
					print("Couldn't unmount: %s" % mount)
					if os.path.exists("/usr/bin/lsof"):
						subprocess.call("/usr/bin/lsof | grep %s" % mount, shell=True)
					print()
				raise MetroError("The following bind mounts could not be unmounted: \n"+mstring)
			else:
				attempt += 1
				self.kill_chroot_pids()
				self.unbind(attempt=attempt)

	def get_active_mounts(self):
		# os.path.realpath should ensure that we are comparing the right thing,
		# if something in the path is a symlink - like /var/tmp -> /foo.
		# Because /proc/mounts will store the resolved path (ie.  /foo/metro)
		# not the regular one (ie. /var/tmp/metro)
		prefix = os.path.realpath(self.settings["path/work"])

		# this used to have a "os.popen("mount")" which is not as accurate as
		# the kernel list /proc/mounts.  The "mount" command relies on
		# /etc/mtab which is not necessarily correct.
		with open("/proc/mounts", "r") as myf:
			mounts = [line.split()[1] for line in myf]
			mounts = [mount for mount in mounts if mount.startswith(prefix)]
			mounts.sort(reverse=True)
			return mounts

# vim: ts=4 sw=4 noet
