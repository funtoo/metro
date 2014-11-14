from .snapshot import SnapshotTarget
from .chroot import ChrootTarget
from .stage import StageTarget
from .virtualbox import VirtualboxTarget
import sys
try:
	import boto.ec2
	from .ec2 import Ec2Target
except ImportError:
	sys.stderr.write("No boto available; ec2 support disabled.\n")

