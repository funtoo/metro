
"""
Builder class for a stage1 installation tarball build.
"""

from catalyst_support import *
from generic_stage_target import *

class stage1_target(generic_stage_target):
	def __init__(self,settings):
		generic_stage_target.__init__(self,settings)
"""
stage_path: $[chroot_path]$[root_path]
root_path: /tmp/stage1root
cleanables: /usr/share/gettext /usr/lib/python2.?/test /usr/lib/python2.?/email /usr/lib/python2.?/lib-tk /usr/share/zoneinfo
"""
	def set_mounts(self):
		# stage_path/proc probably doesn't exist yet, so create it
		if not os.path.exists(self.settings["stage_path"]+"/proc"):
			os.makedirs(self.settings["stage_path"]+"/proc")

		# alter the mount mappings to bind mount proc onto it
		# self.mounts.append("/tmp/stage1root/proc")
		# self.mountmap["/tmp/stage1root/proc"]="/proc"
		# This appears to break baselayout-2.0's makefile, who tries to write to /tmp/stage1root/proc/.keep, so I'm removing it and will see how the build goes
