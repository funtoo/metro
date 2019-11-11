[section steps/ego]

# This will do common prepare steps for ego.conf and leave the prepared ego.conf
# in $[path/work]/etc and set EGO_CONFIG to the path to the new ego.conf file.

prep: [
ego_out_dir=$[path/work]/etc
install -d $ego_out_dir
cat > $ego_out_dir/ego.conf << EOF
[global]
sync_base_url = $[snapshot/source/sync_base_url]
release = $[profile/release]

EOF
if [ "$[snapshot/source/ego.conf?]" = "yes" ]; then
		echo "Installing /etc/ego.conf..."
		cat >> $ego_out_dir/ego.conf << EOF
$[[snapshot/source/ego.conf:lax]]
EOF
fi
export EGO_CONFIG=$ego_out_dir/ego.conf
]

