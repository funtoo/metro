import os, sys, time, types, glob
import subprocess

from metro_support import MetroError

from .base import BaseTarget

class RemoteTarget(BaseTarget):
	def __init__(self, settings,cr):
		BaseTarget.__init__(self, settings, cr)

		self.required_files.append("path/mirror/source")
		if self.settings["release/type"] == "official":
			self.required_files.append("path/mirror/snapshot")

		# vm config
		self.name = self.settings["target/name"]

	def run(self):
		self.check_required_files()
		self.prepare_remote()

		# before we start - clean up any messes
		self.destroy_remote()
		self.clean_path(recreate=True)

		try:
			self.start_remote()
			self.upload_file(glob.glob(self.settings["path/mirror/source"])[0])
			if self.settings["release/type"] == "official":
				self.upload_file(glob.glob(self.settings["path/mirror/snapshot"])[0])
			self.run_script_at_remote("steps/remote/run")
		except:
			self.destroy_remote()
			self.clean_remote()
			raise

		self.wait_for_shutdown()
		self.capture()
		self.run_script("trigger/ok/run", optional=True)

		self.destroy_remote()
		self.clean_remote()
		self.clean_path()

	def ssh_options(self):
		os.chmod(self.ssh_key_path, 0o400)
		return [
			"-o", "StrictHostKeyChecking=no",
			"-o", "UserKnownHostsFile=/dev/null",
			"-o", "GlobalKnownHostsFile=/dev/null'",
			"-i", self.ssh_key_path,
			"-q"
		]

	def ssh_pipe_to_remote(self, cmd, scp=False):
		cmd = ["ssh"] + self.ssh_options() + [self.ssh_uri, cmd]
		return subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=sys.stdout)

	def run_script_at_remote(self, key, optional=False):
		if key not in self.settings:
			if optional:
				return
			raise MetroError("run_script: key '%s' not found." % (key,))

		if type(self.settings[key]) != list:
			raise MetroError("run_script: key '%s' is not a multi-line element." % (key, ))

		print("run_script_at_remote: running %s..." % key)

		ssh = self.ssh_pipe_to_remote("sudo -i /bin/bash -s")
		ssh.stdin.write("\n".join(self.settings[key]))
		ssh.stdin.close()
		ssh.wait()

		if ssh.returncode != 0:
			raise MetroError("Command failure (key %s, return value %s)" % (key, repr(ssh.returncode)))

	def upload_file(self, src_path):
		dst_path = "%s:%s/%s" % (self.ssh_uri, self.remote_upload_path,
				os.path.basename(src_path))

		print("Uploading %s to %s" % (src_path, dst_path))

		cmd = ["scp"] + self.ssh_options() + [src_path, dst_path]
		ssh = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=sys.stdout)
		ssh.stdin.close()
		ssh.wait()

# vim: ts=4 sw=4 noet
