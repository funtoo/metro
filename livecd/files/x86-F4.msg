Hardware options (Page 2):
hda=stroke      This allows you to partition the whole hard disk even when your
                BIOS is unable to handle large disks.  This option is only used
                on machines with an older BIOS.  Replace hda with the device
                that is requiring this option.
ide=nodma       This forces the disabling of DMA in the kernel and is required
                by some IDE chipsets and also by some CDROM drives.  If your
                system is having trouble reading from your IDE CDROM, try this
                option.  This also disables the default hdparm settings from
                being executed.
noapic          This disables the Advanced Programmable Interrupt Controller
                that is present on newer motherboards.  It has been known to
                cause some problems on older hardware.
nodetect        This disables all of the autodetection done by the CD,
                including device autodetection and DHCP probing.  This is
                useful for doing debugging of a failing CD or driver.
nodhcp          This disables DHCP probing on detected network cards.  This is
                useful on networks with only static addresses.
nodmraid        Disables support for device-mapper RAID, such as that used for
                on-board IDE/SATA RAID controllers.
