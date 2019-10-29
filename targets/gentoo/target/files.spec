[section files]

locale.gen: [
# /etc/locale.gen: list all of the locales you want to have on your system
#
# The format of each line:
# <locale> <charmap>
#
# Where <locale> is a locale located in /usr/share/i18n/locales/ and
# where <charmap> is a charmap located in /usr/share/i18n/charmaps/.
#
# All blank lines and lines starting with # are ignored.
#
# For the default list of supported combinations, see the file:
# /usr/share/i18n/SUPPORTED
#
# Whenever glibc is emerged, the locales listed here will be automatically
# rebuilt for you.  After updating this file, you can simply run `locale-gen`
# yourself instead of re-emerging glibc.

en_US.UTF-8 UTF-8
C.UTF-8 UTF-8
]

proxyenv: [
<?python
for x in ["http_proxy","ftp_proxy","RSYNC_PROXY"]:
	if x in os.environ:
		print(x+"=\""+os.environ[x]+"\"")
	else:
		print("# "+x+" is not set")
?>
]

motd: [
$[[files/motd/extra:lax]]

 >>> Release:                       $[target/name]
 >>> Version:                       $[target/version]
 >>> Created by:                    $[release/author]
$[[files/motd/trailer:lax]]

 NOTE: This message can be removed by deleting /etc/motd.

]
