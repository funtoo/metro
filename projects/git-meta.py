#!/usr/bin/python

import os,sys,commands

def die(msg):
	print msg
	sys.exit(1)

if len(sys.argv) != 2:
	die("Please specify a single argument of a Portage tree.")

if not os.path.isdir(sys.argv[1]):
	die("%s is not a directory. I'm looking for a Portage directory." % sys.argv[1])

portdir=sys.argv[1]
portcache = os.path.join(portdir,"metadata/cache")

if not os.path.isdir(portcache):
	die("Can't find Portage cache directory %s" % portcache)

print "Found Portage cache directory: %s" % portcache

gitdir = os.path.join(portdir,".git")

if not os.path.isdir(gitdir):
	die("Portage cache directory %s does not appear to be a git repository.")

os.chdir(portdir)

gitout=os.popen("git ls-files -m").readlines()

if not len(gitout):
	print "Did not find any locally modified files."

if os.path.exists("/tmp/localmeta.out"):
	os.unlink("/tmp/localmeta.out")
localout = open("/tmp/localmeta.out","w")
for x in gitout:
	if x[-8:-1] != ".ebuild":
		continue
	slash = x.split("/")
	if slash[0] == "eclass":
		die("You have locally modified eclasses. Will not update cache.")
	if len(slash) != 3:
		# not at proper depth
		continue
	localkey = slash[0] + "/" + slash[2][:-8]
	localout.write("/"+localkey+"\n")
localout.close()

if os.path.exists("/tmp/localmeta.out"):
	args = "--exclude-from /tmp/localmeta.out %s" % portcache 
else:
	args = portcache
cmdout=commands.getstatusoutput("rsync -av "+args+"/ /var/cache/edb/dep" + portdir + "/ --exclude /sec-policy/")
if cmdout[0] == 0:
	print "Metadata update completed successfully"
else:
	die("Metadata update didn't complete successfully")
