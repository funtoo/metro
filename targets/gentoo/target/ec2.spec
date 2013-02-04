[collect ./remote.spec]

[section target]

class: ec2

[section steps/remote]

postboot: [
yum -y install openssh-clients
]

setup: [
pushd /etc/yum.repos.d
wget http://download.opensuse.org/repositories/home:srs5694/CentOS_CentOS-6/home:srs5694.repo
popd

yum -y install git gdisk parted xfsprogs e2fsprogs lvm2
]

[section quickstart]

profile: [
. profiles/common/base.sh
. profiles/common/ec2.sh

stage_uri file://$(ls -1 /tmp/$(basename "$[path/mirror/source]"))
tree_type snapshot file://$(ls -1 /tmp/$(basename "$[path/mirror/snapshot]"))

part $[ec2/instance/device/name] 1 fd00 1G
part $[ec2/instance/device/name] 2 fd00

lvm_volgroup vg /dev/$[ec2/instance/device/name]2

format /dev/$[ec2/instance/device/name]1 ext3

mountfs /dev/$[ec2/instance/device/name]1 ext3 /

shutdown

post_install() {
    setup_pv_grub /dev/$[ec2/instance/device/name]1
}
]

[section trigger]

ok/run: [
#!/bin/bash

install -d $[path/mirror/target/control]/version/$[target/class] || exit 1
echo "$[target/version]" > $[path/mirror/target/control]/version/$[target/class]/$[remote/target/name].$[ec2/region] || exit 1

$[[trigger/ok/symlink]]
]
