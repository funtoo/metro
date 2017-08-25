from .chroot import ChrootTarget

class StageTarget(ChrootTarget):
	def __init__(self, settings, cr):
		ChrootTarget.__init__(self, settings, cr)

		# stages need a snapshot to install packages
		if self.settings["release/type"] == "official":
			self.required_files.append("path/mirror/snapshot")

		# define gentoo specific mounts
		if "path/distfiles" in self.settings:
			self.mounts["/var/cache/portage/distfiles"] = self.settings["path/distfiles"]

	def run(self):
		ChrootTarget.run(self)

		# now, we want to clean up our build-related caches, if configured to do so:
		if "metro/options" in self.settings:
			if "clean/auto" in self.settings["metro/options"].split():
				if "path/cache/build" in self.settings:
					self.clean_path(self.settings["path/cache/build"])

# vim: ts=4 sw=4 noet
