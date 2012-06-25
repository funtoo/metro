# This file contains snapshot settings that are used across *all*
# targets, including stages.

[section portage]

name: portage
name/full: $[:name]-$[target/version]

[section path/mirror]

# This is the actual snapshot that the stages use and the snapshot targets create
snapshot: $[]/$[:snapshot/subpath]/$[portage/name/full].tar.$[snapshot/compression]
