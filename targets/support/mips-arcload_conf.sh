#!/bin/bash


#// Variables holding the data of the arcload config file, arc.cf
#//-----------------------------------------------------------------------------

topofconfig="# Gentoo/MIPS LiveCD Prototype\n# ARCLoad Configuration\n\ndetect;\n\n\
# Global options\ncomment\t\t\"Global Options (not bootable):\\\n\\\r\\\n\\\r\";\n\n"

serial="serial {\n\
\tbaud=9600 {\n\
\t\tport1 {\n\
\t\t\tdescription\t\"Serial Console, Port 1, 9600 Baud\";\n\
\t\t\timage\t\t\"\";\n\
\t\t\tappend\t\t\"console=ttyS0,9600\" \"nox\";\n\
\t\t}\n\n\
\t\tport2 {\n\
\t\t\tdescription\t\"Serial Console, Port 2, 9600 Baud\";\n\
\t\t\timage\t\t\"\";\n\
\t\t\tappend\t\t\"console=ttyS1,9600\" \"nox\";\n\
\t\t}\n\
\t}\n\n\
\tbaud=38400 {\n\
\t\tport1 {\n\
\t\t\tdescription\t\"Serial Console, Port 1, 38400 Baud\";\n\
\t\t\timage\t\t\"\";\n\
\t\t\tappend\t\t\"console=ttyS0,38400\" \"nox\";\n\
\t\t}\n\n\
\t\tport2 {\n\
\t\t\tdescription\t\"Serial Console, Port 2, 38400 Baud\";\n\
\t\t\timage\t\t\"\";\n\
\t\t\tappend\t\t\"console=ttyS1,38400\" \"nox\";\n\
\t\t}\n\
\t}\n\
}\n\n\n"

dbg="debug {\n\
\tdescription\t\"Debug Shell\";\n\
\timage\t\t\"\";\n\
\tappend\t\t\"real_root=shell\" \"nox\";\n}\n\n"		

cmt1="comment\t\t\"\\\n\\\n\";\n\
comment\t\t\"Bootable Images & Options:\\\n\\\r\\\n\\\r\";\n"

ip22base="# IP22 R4x00 Systems (Indy/Indigo2)\n\
ip22 {\n\
\tdescription\t\"SGI Indy/Indigo2\";\n\
\tappend\t\t\"real_root=/dev/sr0\" \"cdroot=/dev/loop0\" \"looptype=sgimips\" \"nosound\";\n"

ip22r4k="\tr4000 r4600 r4700 {\n\
\t\tdescription\t\"\\\tR4x00 CPU\";\n\
\t\timage system\t\"/ip22r4k\";\n\
\t}\n"

ip22r5k="\tr5000 {\n\
\t\tdescription\t\"\\\tR5000 CPU\";\n\
\t\timage system\t\"/ip22r5k\";\n\
\t}\n"

ip22vid="\tvideo {\n\
\t\tdescription\t\"\\\tNewport Console\\\n\\\r\";\n\
\t\tappend\t\t\"console=tty0\" \"ip22\";\n\
\t}\n"

ip22x="}\n\n\n"

ip27base="# IP27 Origin 200/2000\n\
ip27 {\n\
\tdescription\t\"SGI Origin 200/2000\\\n\\\r\";\n\
\timage system\t\"/ip27r10k\";\n\
\tappend\t\t\"real_root=/dev/sr0\" \"cdroot=/dev/loop0\" \"looptype=sgimips\" \"nox\" \"nosound\";\n\
}\n\n\n"

ip28base="# IP28 Indigo2 Impact R10000\n\
ip28 {\n\
\tdescription\t\"SGI Indigo2 Impact R10000\\\n\\\r\";\n\
\timage system\t\"/ip28r10k\";\n\
\tappend\t\t\"real_root=/dev/sr0\" \"cdroot=/dev/loop0\" \"looptype=sgimips\" \"nosound\" \"ip28\";\n\
}\n\n\n"

ip30base="# IP30 Octane\n\
ip30 {\n\
\tdescription\t\"SGI Octane\";\n\
\timage system\t\"/ip30r10k\";\n\
\tappend\t\t\"real_root=/dev/sr0\" \"cdroot=/dev/loop0\" \"looptype=sgimips\" \"nosound\" \"ip30\";\n\n\
\tnosmp {\n\
\t\tdescription\t\"\\\tUniprocessor Mode\";\n\
\t\tappend\t\t\"nosmp\";\n\
\t}\n\n\
\tvideo {\n\
\t\tdescription\t\"\\\tImpactSR/VPro Console\\\n\\\r\";\n\
\t\tappend\t\t\"console=tty0\" \"ip30\";\n\
\t}\n\
}\n\n\n"

ip32base="# IP32 O2\n\
ip32 {\n\
\tdescription\t\"SGI O2\";\n\
\tappend\t\t\"real_root=/dev/sr0\" \"cdroot=/dev/loop0\" \"looptype=sgimips\" \"nosound\";\n"

ip32r5k="\tr5000 {\n\
\t\tdescription\t\"\\\tR5000 CPU\";\n\
\t\timage system\t\"/ip32r5k\";\n\
\t}\n"

ip32rm5k="\trm5200 {\n\
\t\tdescription\t\"\\\tRM5200 CPU\";\n\
\t\timage system\t\"/ip32rm5k\";\n\
\t}\n"

ip32rm7k="\trm7000 {\n\
\t\tdescription\t\"\\\tRM7000 CPU\";\n\
\t\timage system\t\"/ip32rm7k\";\n\
\t}\n"

ip32r10k="\tr10000 r12000 {\n\
\t\tdescription\t\"\\\tR10000/R12000 CPU\";\n\
\t\timage system\t\"/ip32r10k\";\n\
\t}\n"

ip32vid="\tvideo=640x480 {\n\
\t\tdescription\t\"\\\tGBEFB Console 640x480 16bpp/75Hz\";\n\
\t\tappend\t\t\"console=tty0 video=gbefb:640x480-16@75\" \"ip32\";\n\
\t}\n\n\
\tvideo=800x600 {\n\
\t\tdescription\t\"\\\tGBEFB Console 800x600 16bpp/75Hz\";\n\
\t\tappend\t\t\"console=tty0 video=gbefb:800x600-16@75\" \"ip32\";\n\
\t}\n\n\
\tvideo=1024x768 {\n\
\t\tdescription\t\"\\\tGBEFB Console 1024x768 16bpp/75Hz\";\n\
\t\tappend\t\t\"console=tty0 video=gbefb:1024x768-16@75\" \"ip32\";\n\
\t}\n\n\
\tvideo=1280x1024 {\n\
\t\tdescription\t\"\\\tGBEFB Console 1280x1024 16bpp/75Hz\\\n\\\r\\\n\\\r\\\n\\\r\";\n\
\t\tappend\t\t\"console=tty0 video=gbefb:1280x1024-16@75\" \"ip32\";\n\
\t}\n"

ip32x="}\n\n\n"

cmt2="comment\t\t\"To boot an image, set \`OSLoadFilename\` to the to following sequence\";\n\
comment\t\t\"depending on your desired options (examples):\\\n\\\r\\\n\\\r\";\n\
comment\t\t\"IP32 R5000 w/ 38400 serial:\\\n\\\r\";\n\
comment\t\t\"setenv OSLoadFilename ip32(r5000,serial-h)\\\n\\\r\\\n\\\r\";\n\
comment\t\t\"IP32 RM5200 w/ GBEFB Console @ 800x600:\\\n\\\r\";\n\
comment\t\t\"setenv OSloadFilename ip32(rm5200,video=800x600)\\\n\\\r\\\n\\\r\";\n\
comment\t\t\"IP30 w/ no SMP and video:\\\n\\\r\";\n\
comment\t\t\"setenv OSLoadFilename ip30(nosmp,video)\\\n\\\r\\\n\\\r\\\n\\\r\";\n\
comment\t\t\"Once \`OSLoadFilename\` is set, execute:\\\n\\\r\\\n\\\r\";\n\
comment\t\t\"\`sashARCS\` for IP22/IP32\\\n\\\r\\\n\\\r\";\n\
comment\t\t\"\`sash64\` for IP27/IP28/IP30\\\n\\\r\\\n\\\r\";\n\n"

#//-----------------------------------------------------------------------------
