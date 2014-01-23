from .base import BaseTarget

class SnapshotTarget(BaseTarget):
    def __init__(self, settings):
        BaseTarget.__init__(self, settings)

    def run(self):
        if not self.target_exists("path/mirror/snapshot"):
            BaseTarget.run(self)
        self.run_script("trigger/ok/run", optional=True)

# vim: ts=4 sw=4 et
