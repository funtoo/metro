
. ${clst_sharedir}/targets/support/functions.sh
. ${clst_sharedir}/targets/support/filesystem-functions.sh

# Make the directory if it doesnt exist
mkdir -p $1

loopret=1
case ${clst_fstype} in
	normal)
		create_normal_loop $1
		loopret=$?
	;;
	zisofs)
		create_zisofs $1
		loopret=$?
	;;
	noloop)
		create_noloop $1
		loopret=$?
	;;
	squashfs)
		create_squashfs $1
		loopret=$?
	;;
	jffs)
		create_jffs $1
		loopret=$?
	;;
	jffs2)
		create_jffs2 $1
		loopret=$?
	;;
	cramfs)
		create_cramfs $1
		loopret=$?
	;;
esac

if [ ${loopret} = "1" ]
then
	die "Filesystem not setup"
fi
exit $loopret
