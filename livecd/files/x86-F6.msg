Volume/Device Management:
dodevfs         This enables the deprecated device filesystem on 2.6 systems.
                You will also need to use noudev for this to take effect.
                Since devfs is the only option with a 2.4 kernel, this option
                has no effect if booting a 2.4 kernel.
doevms2         This enables support for IBM's pluggable EVMS, or Enterprise
                Volume Management System.  This is not safe to use with lvm2.
dolvm2          This enables support for Linux's Logical Volume Management.
                This is not safe to use with evms2.
noudev          This disables udev support on 2.6 kernels.  This option
                requires that dodevfs is used.  Since udev is not an option for
                2.4 kernels, this options has no effect if booting 2.4 kernels.
unionfs         Enables support for Unionfs on supported CD images.  This will
                create a writable Unionfs overlay in a tmpfs, allowing you to
                change any file on the CD.
unionfs=X       Enables support for Unionfs on supported CD images.  This will
                create a writable Unionfs overlay on the device you specify.
                The device must be formatted with a filesystem recognized and
                writable by the kernel.
