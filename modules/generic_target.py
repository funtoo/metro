from catalyst_support import *
import os

class generic_target:

	def __init__(self,settings):
		self.settings=settings
		self.env={}
		self.env["PATH"]="/bin:/sbin:/usr/bin:/usr/sbin"

	def require(self,mylist):
		missing=self.settings.missing(mylist)
		if missing:
			raise CatalystError,"Missing required configuration values "+`missing`
