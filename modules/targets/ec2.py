import os, sys, time, types, glob
import subprocess

import boto.ec2
from boto.ec2.blockdevicemapping import BlockDeviceType
from boto.ec2.blockdevicemapping import BlockDeviceMapping

from metro_support import MetroError, ismount

from .remote import RemoteTarget

class Ec2Target(RemoteTarget):
	def __init__(self, settings, cr):
		RemoteTarget.__init__(self, settings, cr)

		# ec2 specifics
		self.region = self.settings["ec2/region"]
		self.ec2 = boto.ec2.connect_to_region(self.region)

		if self.settings["target/arch_desc"] == "x86-64bit":
			self.arch = "x86_64"
		else:
			self.arch = "i386"

	def prepare_remote(self):
		if self.settings["target/arch_desc"] not in ["x86-64bit", "x86-32bit"]:
			raise MetroError("EC2 target class only supports x86 targets")

		self.clean_remote()

		self.ec2.create_security_group(self.name, self.name)
		self.ec2.authorize_security_group(group_name=self.name,
				ip_protocol='tcp',
				from_port=22, to_port=22,
				cidr_ip='0.0.0.0/0')

		self.ssh_key_path = "%s/%s.pem" % (self.settings["path/tmp"],
				self.name)

		try:
			os.unlink(self.ssh_key_path)
		except:
			pass

		key_pair = self.ec2.create_key_pair(self.name)
		key_pair.save(self.settings["path/tmp"])

	def clean_remote(self):
		try:
			self.ec2.delete_security_group(self.name)
		except boto.exception.EC2ResponseError:
			pass

		try:
			self.ec2.delete_key_pair(self.name)
		except boto.exception.EC2ResponseError:
			pass

	def start_remote(self):
		self.get_bootstrap_kernel()
		self.get_bootstrap_image()

		# create EBS volume for /mnt/gentoo
		device = BlockDeviceType()
		device.size = self.settings["ec2/instance/device/size"]
		device.delete_on_termination = True

		mapping = BlockDeviceMapping()
		self.root_device = "/dev/" + self.settings["ec2/instance/device/name"]
		mapping[self.root_device] = device

		# start bootstrapping instance
		reservation = self.ec2.run_instances(self.bootstrap_image.id,
				kernel_id=self.bootstrap_kernel.id,
				instance_type=self.settings["ec2/instance/type"],
				security_groups=[self.name],
				key_name=self.name,
				block_device_map=mapping)

		self.instance = reservation.instances[0]

		sys.stdout.write("waiting for instance to come up ..")
		while self.instance.update() != 'running':
			sys.stdout.write(".")
			sys.stdout.flush()
			time.sleep(5)
		sys.stdout.write("\n")
		time.sleep(120)

		self.ssh_uri = "ec2-user@" + self.instance.public_dns_name
		self.remote_upload_path = "/tmp"

		# enable sudo without a tty
		cmd = "sudo sed -i -e '/requiretty/d' /etc/sudoers"
		cmd = ["ssh", "-t"] + self.ssh_options() + [self.ssh_uri, cmd]
		ssh = subprocess.Popen(cmd)
		ssh.wait()

		self.run_script_at_remote("steps/remote/postboot")

	def wait_for_shutdown(self):
		sys.stdout.write("waiting for instance to shutdown ..")
		while self.instance.update() != 'stopped':
			sys.stdout.write(".")
			sys.stdout.flush()
			time.sleep(5)
		sys.stdout.write("\n")

	def capture(self):
		volume = self.ec2.get_all_volumes(filters={
			'attachment.instance-id': self.instance.id,
			'attachment.device': self.root_device,
		})[0]

		snapshot = self.ec2.create_snapshot(volume.id)

		sys.stdout.write("waiting for snapshot to complete ..")
		while snapshot.status != 'completed':
			sys.stdout.write(".")
			sys.stdout.flush()
			time.sleep(5)
			snapshot.update()
		sys.stdout.write("\n")

		# create EBS mapping
		device = BlockDeviceType()
		device.snapshot_id = snapshot.id

		mapping = BlockDeviceMapping()
		mapping['/dev/sda'] = device

		self.get_instance_kernel()
		image = self.ec2.register_image(name=self.name, description=self.name,
				architecture=self.arch, kernel_id=self.instance_kernel.id,
				root_device_name='/dev/sda', block_device_map=mapping)

		if self.settings["target/permission"] == "public":
			self.ec2.modify_image_attribute(image, groups='all')

		with open(self.settings["path/mirror/target"], "w") as fd:
			cmd = [
				"ec2-run-instances",
				"--region", self.region,
				"--instance-type", "t1.micro",
				image,
			]
			fd.write(" ".join(cmd))
			fd.write("\n")

	def destroy_remote(self):
		if hasattr(self, 'instance'):
			self.ec2.terminate_instances([self.instance.id])

	def get_bootstrap_kernel(self):
		kernels = self.ec2.get_all_images(owners=['amazon'], filters={
			'image-type': 'kernel',
			'architecture': self.arch,
			'manifest-location': '*pv-grub-hd0_*'
		})

		self.bootstrap_kernel = sorted(kernels, key=lambda k: k.location)[-1]
		print("bootstrap kernel-id: " + self.bootstrap_kernel.id)

	def get_instance_kernel(self):
		kernels = self.ec2.get_all_images(owners=['amazon'], filters={
			'image-type': 'kernel',
			'architecture': self.arch,
			'manifest-location': '*pv-grub-hd00_*'
		})

		self.instance_kernel = sorted(kernels, key=lambda k: k.location)[-1]
		print("instance kernel-id: " + self.instance_kernel.id)

	def get_bootstrap_image(self):
		images = self.ec2.get_all_images(filters={
			'image-type': 'machine',
			'architecture': self.arch,
			'manifest-location': 'amazon/amzn-ami-*',
			'root-device-type': 'ebs',
			'virtualization-type': 'paravirtual',
			'kernel-id': self.bootstrap_kernel.id
		})

		self.bootstrap_image = images[-1]
		print("bootstrap image-id: " + self.bootstrap_image.id)

# vim: ts=4 sw=4 noet
