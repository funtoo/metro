Hardware options (Page 1):
acpi=on         This loads support for ACPI and also causes the acpid daemon to
                be started by the CD on boot.  This is only needed if your
                system requires ACPI to function properly.  This is not
                required for Hyperthreading support.
acpi=off        Completely disables ACPI.  This is useful on some older systems
                and is also a requirement for using APM.  This will disable any
                Hyperthreading support of your processor.
console=X       This sets up serial console access for the CD.  The first
                option is the device, usually ttyS0 on x86, followed by any
                connection options, which are comma separated.  The default
                options are 9600,8,n,1.
dmraid=X        This allows for passing options to the device-mapper RAID
                subsystem.  Options should be encapsulated in quotes.
doapm           This loads APM driver support.  This requires you to also use
                acpi=off.
dopcmcia        This loads support for PCMCIA and Cardbus hardware and also
                causes the pcmcia cardmgr to be started by the CD on boot.
                This is only required when booting from PCMCIA/Cardbus devices.
doscsi          This loads support for most SCSI controllers.  This is also a
                requirement for booting most USB devices, as they use the SCSI
                subsystem of the kernel.
