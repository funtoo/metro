Other options:
debug           Enables debugging code.  This might get messy, as it displays
                a lot of data to the screen.
docache         This caches the entire runtime portion of the CD into RAM,
                which allows you to umount /mnt/cdrom and mount another CDROM.
                This option requires that you have at least twice as much
                available RAM as the size of the CD.
doload=X        This causes the initial ramdisk to load any module listed, as
                well as dependencies.  Replace X with the module name.
                Multiple modules can be specified by a comma-separated list.
noload=X        This causes the initial ramdisk to skip the loading of a
                specific module that may be causing a problem.  Syntax matches
                that of doload.
nox             This causes an X-enabled LiveCD to not automatically start X,
                but rather, to drop to the command line instead.
scandelay       This causes the CD to pause for 10 seconds during certain
                portions the boot process to allow for devices that are slow to
                initialize to be ready for use.
scandelay=X     This allows you to specify a given delay, in seconds, to be
                added to certain portions of the boot process to allow for
                devices that are slow to initialize to be ready for use.
                Replace X with the number of seconds to pause.
