
"""
Builder class for a stage2 installation tarball build.
"""

from catalyst_support import *
from generic_stage_target import *

class stage2_target(generic_stage_target):
	def __init__(self,settings):
		generic_stage_target.__init__(self,settings)

"""
source_path: $[storedir]/builds/$[source_subpath].tar.bz2
cleanables: $[cleanables] /etc/portage
"""
