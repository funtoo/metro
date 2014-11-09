from .base import BaseTarget

class SnapshotTarget(BaseTarget):
	def __init__(self, settings):
		BaseTarget.__init__(self, settings)

	def run(self):
		self.run()
		self.run_script("trigger/ok/run", optional=True)


# vim: ts=4 sw=4 noet
