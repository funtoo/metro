[section steps]

capture: [
#!/bin/bash
if [ "$(uname -m)" == 'i686' ]; then
  export ARCH="i386"
else
  export ARCH="x86_64"
fi

ec2-bundle-vol \
	-u $[ec2/owner-id] \
    	-k $[path/ec2/key] \
	-c $[path/ec2/crt] \
    	--no-inherit \
	-r $ARCH \
	--kernel $[ec2/kernel] \
	-d `dirname $[path/mirror/target]` \
    	-v $[path/chroot/stage] \
	--fstab $[path/chroot/stage]/etc/fstab

export BUNDLE=gentoo-$(\
wget -q -O - http://169.254.169.254/2008-02-01/meta-data/instance-type\
)-$(date +%Y%m%d)
echo $BUNDLE

# NOW: Create an S3 bucket w/ $BUNDLE as the name
ec2-upload-bundle \
    	-a $[ec2/access-key] \
	-s $[ec2/private-access-key] \
    	--retry \
	--batch \
	-b $BUNDLE \ 
	-m /mnt/image.manifest.xml

ec2-register \
    	-K $[path/ec2/key] \
	-C $[path/ec2/crt] \
    	$BUNDLE/image.manifest.xml

ec2-modify-image-attribute \
  	-K /etc/ssl/ec2/key.pem \
	-C /etc/ssl/ec2/crt.pem \
  	-l \
	-a all \
  	<ami-id>
]
