[collect ./source/seed.spec]
[collect ./target/stage3.spec]
[collect ./steps/capture/tar.spec]

[section steps]

chroot/run: [
#!/bin/bash
$[[steps/setup]]
#emerge --oneshot $eopts portage || exit 1
export USE="$[portage/USE] bindist"
emerge $eopts --deep --newuse -u @world 
if [ $? -ne 0 ]; then
	# maybe we did a perl upgrade, and we need to fix-up perl modules that are currently broken and causing perl
	# DEPEND to not work.
	# this was migrated *into* perl itself, and perl-cleaner doesn't handle it well:
	emerge -C perl-core/Scalar-List-Utils
	# perl-cleaner will now do its thing and even emerge virtual/Scalar-List-Utils if missing, like a good boy!
	perl-cleaner --all || exit 1
	# perl should be upgraded at this point, so perl and its modules should be happy, so they shouldn't be in an intermediate
	# state when we do the following:
	# continue where we left off...
	emerge $eopts --deep --newuse -u @world
fi
emerge --deep --newuse -u $eopts $[emerge/packages/force:zap] || exit 2
emerge --deep --newuse -u $eopts $[emerge/packages:zap] || exit 1
if [ "`emerge --list-sets | grep preserved-rebuild`" = "preserved-rebuild" ]
then
	emerge $eopts @preserved-rebuild || exit 3
fi

# Clean older debian-sources slotsand keep highest installed, which will reduce resulting stage
emerge --prune sys-kernel/debian-sources || exit 1

# run perl-cleaner to ensure all modules rebuilt after a major
# perl update, fix FL-122
perl-cleaner --all || exit 1
]

[section portage]

ROOT: /
