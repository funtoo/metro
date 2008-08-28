# probably specific to the build
#profile: default/linux/$[arch]/2008.0

# specific to the stage
#root_path: /
#controller_file: $[sharedir]/targets/$[target]/$[target]-controller.sh
#action_sequence: unpack unpack_snapshot config_profile_link setup_confdir portage_overlay base_dirs bind chroot_setup setup_environment run_local preclean unbind clean
#cleanables: /etc/resolv.conf /var/tmp/* /tmp/* /root/* /usr/portage
#USE: $[HOSTUSE]

# specific to the mirror
#target_subpath: $[rel_type]/$[target]-$[subarch]-$[version]
#snapshot_path: $[storedir]/snapshots/$[portname]-$[snapshot].tar.bz2
#source_path: $[storedir]/builds/$[source_subpath].tar.bz2
#chroot_path: $[storedir]/tmp/$[target_subpath]
#target_path: $[storedir]/builds/$[target_subpath].tar.bz2
#destpath: $[chroot_path]$[root_path]
#stage_path: $[chroot_path]

# mirror - another way to do it

#source: stage2
#target: stage3

storedir: /home/mirror/linux
snapshot: $[storedir]/snapshots/$[portname]-$[version].tar.bz2
source_stage: $[storedir]/$[subarch]/$[portname]-$[subarch]-$[lastdate]/$[source]-$[lastdate].tar.bz2
dest_stage: $[storedir]/$[subarch]/$[portname]-$[subarch]-$[version]/$[target]-$[version].tar.bz2

workdir: /var/tmp/catalyst-$[portname]-$[subarch]-$[version]

