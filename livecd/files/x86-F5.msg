Hardware options (Page 3):
nofirewire      This disables the loading of Firewire modules.  This should
                only be necessary if your Firewire hardware is causing
                a problem with booting the CD.
nogpm           This diables gpm console mouse support.
nohotplug       This disables the loading of the hotplug and coldplug init
                scripts at boot.  This is useful for doing debugging of a
                failing CD or driver.
nokeymap        This disables the keymap selection used to select non-US
                keyboard layouts.
nolapic         This disables the local APIC on Uniprocessor kernels.
nosata          This disables the loading of Serial ATA modules.  This is used
                if your system is having problems with the SATA subsystem.
nosmp           This disables SMP, or Symmetric Multiprocessing, on SMP-enabled
                kernels.  This is useful for debugging SMP-related issues with
                certain drivers and motherboards.
nosound         This disables sound support and volume setting.  This is useful
                for systems where sound support causes problems.
nousb           This disables the autoloading of USB modules.  This is useful
                for debugging USB issues.
slowusb         This adds some extra pauses into the boot process for slow
                USB CDROMs, like in the IBM BladeCenter.
