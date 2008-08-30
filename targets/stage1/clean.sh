#!/bin/bash
# Zap all .pyc and .pyo files
find . -iname "*.py[co]" -exec rm -f {} \;
# Cleanup all .a files except libgcc.a, *_nonshared.a and /usr/lib/portage/bin/*.a
find . -type f -iname "*.a" | grep -v 'libgcc.a' | grep -v 'nonshared.a' | grep -v '/usr/lib/portage/bin/' | grep -v 'libgcc_eh.a' | xargs rm -f
find etc/ -maxdepth 1 -name "*-" | xargs rm -f 
rm -rf /usr/share/gettext /usr/lib/python2.?/test /usr/lib/python2.?/email /usr/lib/python2.?/lib-tk/usr/share/zoneinfo /usr/share/{man,doc,info}/*
