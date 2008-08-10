
"""
Builder class for stage4.
"""

from catalyst_support import *
from generic_stage_target import *

class stage4_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=["stage4/packages"]
		self.valid_values=self.required_values[:]
		self.valid_values.extend(["stage4/use","boot/kernel",\
				"stage4/root_overlay","stage4/fsscript",\
				"stage4/gk_mainargs","splash_theme","splash_type",\
				"portage_overlay","stage4/rcadd","stage4/rcdel",\
				"stage4/linuxrc","stage4/unmerge","stage4/rm","stage4/empty"])
		generic_stage_target.__init__(self,spec,addlargs)

	def set_cleanables(self):
		self.settings["cleanables"]=["/var/tmp/*","/tmp/*"]

	def set_action_sequence(self):
		self.settings["action_sequence"]=["unpack","unpack_snapshot",\
					"config_profile_link","setup_confdir","portage_overlay",\
					"bind","chroot_setup","setup_environment","build_packages",\
					"build_kernel","bootloader","root_overlay","fsscript",\
					"preclean","rcupdate","unmerge","unbind","remove","empty",\
					"clean"]

#		if self.settings.has_key("TARBALL") or \
#			not self.settings.has_key("FETCH"):
		if not self.settings.has_key("FETCH"):
			self.settings["action_sequence"].append("capture")
		self.settings["action_sequence"].append("clear_autoresume")

def register(foo):
	foo.update({"stage4":stage4_target})
	return foo

