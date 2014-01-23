from .chroot import ChrootTarget

class StageTarget(ChrootTarget):
    def __init__(self, settings):
        ChrootTarget.__init__(self, settings)

        # stages need a snapshot to install packages
        self.required_files.append("path/mirror/snapshot")

        # define gentoo specific mounts
        if self.settings.has_key("path/distfiles"):
            self.mounts["/usr/portage/distfiles"] = self.settings["path/distfiles"]

    def run(self):
        ChrootTarget.run(self)

        # now, we want to clean up our build-related caches, if configured to do so:
        if self.settings.has_key("metro/options"):
            if "clean/auto" in self.settings["metro/options"].split():
                if self.settings.has_key("path/cache/build"):
                    self.clean_path(self.settings["path/cache/build"])

# vim: ts=4 sw=4 et
