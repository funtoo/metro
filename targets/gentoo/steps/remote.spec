[collect ../snapshot/global.spec]

[section steps/remote]

run: [
#!/bin/bash

$[[steps/remote/setup:lax]]

git clone -b $[quickstart/branch] $[quickstart/remote] /tmp/quickstart
pushd /tmp/quickstart

cat <<EOF > profiles/$[target/name].sh
$[[quickstart/profile]]
EOF

./quickstart -v -d profiles/$[target/name].sh
popd

true
]
