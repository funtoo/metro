[section files]

epro_getarch: [
#!/usr/bin/python3

import sys
import json

lines = sys.stdin.readlines()
try:
    j = json.loads("".join(lines))
except ValueError:
    sys.exit(1)
if "arch" in j and len(j["arch"]):
    a = j["arch"][0]
    if "path" in a:
        print(a["path"])
        sys.exit(0)
sys.exit(1)
]

[section steps]

epro_setup: [
# make sure we have the latest ego.
emerge -u --oneshot ego
# regen profiles
epro update
cat > /tmp/epro_getarch.py << "EOF"
$[[files/epro_getarch]]
EOF
archdir="$(epro show-json | python3 /tmp/epro_getarch.py)"
echo "$archdir" > /tmp/archdir
if [ -n "$archdir" ] && [ -e "$archdir/toolchain-version" ]; then
	# We will use toolchain_version to set a sub-directory for binary packages. This way, bumping the
	# toolchain version in the profile forces metro to rebuild all binary packages -- which is what we
	# want when we have a new toolchain, to flush out old, now stable .tbz2 files.
	toolchain_version="$(cat $archdir/toolchain-version)"
fi
]


