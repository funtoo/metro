import os, sys, types
from glob import glob

from catalyst_support import MetroError, spawn, spawn_bash, ismount

CMDS = {
    "bash": "/bin/bash",
    "chroot": "/usr/bin/chroot",
    "install": "/usr/bin/install",
    "kill": "/bin/kill",
    "linux32": "/usr/bin/linux32",
    "mount": "/bin/mount",
    "rm": "/bin/rm",
}

class target:
    def run(self):
        self.clean_path(recreate=True)

        self.run_script("steps/run")
        if self.settings.has_key("trigger/ok/run"):
            self.run_script("trigger/ok/run")

        self.clean_path()

    def run_script(self, key, chroot=None, optional=True):
        if not self.settings.has_key(key):
            if optional:
                raise MetroError, "run_script: key '%s' not found." % (key,)
            else:
                return

        if type(self.settings[key]) != types.ListType:
            raise MetroError, "run_script: key '%s' is not a multi-line element." % (key, )

        print
        print "run_script: running %s..." % key
        print

        os.environ["PATH"] = self.env["PATH"]

        if chroot:
            chrootfile = "/tmp/"+key+".metro"
            outfile = chroot+chrootfile
        else:
            outfile = self.settings["path/tmp"]+"/pid/"+repr(os.getpid())

        outdir = os.path.dirname(outfile)

        if not os.path.exists(outdir):
            os.makedirs(outdir)
        outfd = open(outfile,"w")

        for line in self.settings[key]:
            outfd.write(line + "\n")

        outfd.close()
        os.chmod(outfile, 0755)

        cmds = []
        if chroot:
            if self.settings["target/arch"] == "x86" and os.uname()[4] == "x86_64":
                cmds = [CMDS["linux32"], CMDS["chroot"]]
            else:
                cmds = [CMDS["chroot"]]
            cmds.append(chroot)
            cmds.append(chrootfile)
        else:
            cmds.append(outfile)

        retval = spawn(cmds, env=self.env )
        if retval != 0:
            raise MetroError, "Command failure (key %s, return value %s) : %s" % ( key, repr(retval), " ".join(cmds))

        # it could have been cleaned by our outscript, so if it exists:
        if os.path.exists(outfile):
            os.unlink(outfile)

    def target_exists(self, key):
        if self.settings.has_key("metro/options") and "replace" in self.settings["metro/options"].split():
            if os.path.exists(self.settings[key]):
                print "Removing existing file %s..." % self.settings[key]
                self.cmd(CMDS["rm"] + " -f " + self.settings[key])
            return False
        elif os.path.exists(self.settings[key]):
            print "File %s already exists - skipping..." % self.settings[key]
            return True
        else:
            return False

    def __init__(self, settings):
        self.settings = settings
        self.env = {}
        self.env["PATH"] = "/bin:/sbin:/usr/bin:/usr/sbin"

    def clean_path(self, path=None, recreate=False):
        if path == None:
            path = self.settings["path/work"]
        if os.path.exists(path):
            print "Cleaning up %s..." % path
        self.cmd(CMDS["rm"]+" -rf "+path)
        if recreate:
            # This line ensures that the root /var/tmp/metro path has proper 0700 perms:
            self.cmd(CMDS["install"]+" -d -m 0700 -g root -o root " + self.settings["path/tmp"])
            # This creates the directory we want.
            self.cmd(CMDS["install"]+" -d -m 0700 -g root -o root "+path)
            # The 0700 perms prevent Metro-generated /tmp directories from being abused by others -
            # because they are world-writeable, they could be used by malicious local users to
            # inject arbitrary data/executables into a Metro build.

    def cmd(self, mycmd, myexc="", badval=None):
        print "Executing \""+mycmd+"\"..."
        #print "Executing \""+mycmd.split(" ")[0]+"\"..."
        try:
            sys.stdout.flush()
            retval = spawn_bash(mycmd, self.env)
            if badval:
                # This code is here because tar has a retval of 1 for non-fatal warnings
                if retval == badval:
                    raise MetroError, myexc
            else:
                if retval != 0:
                    raise MetroError, myexc
        except:
            raise

class chroot(target):

    def get_chroot_pids(self):
        cdir = self.settings["path/work"]
        pids = []
        for pid in os.listdir("/proc"):
            if not os.path.isdir("/proc/"+pid):
                continue
            try:
                mylink = os.readlink("/proc/"+pid+"/exe")
            except OSError:
                # not a pid directory
                continue
            if mylink[0:len(cdir)] == cdir:
                pids.append([pid, mylink])
        return pids

    def kill_chroot_pids(self):
        for pid, mylink in self.get_chroot_pids():
            print "Killing process "+pid+" ("+mylink+")"
            self.cmd(CMDS["kill"]+" -9 "+pid)

    def run_script_in_chroot(self, key, chroot=None, optional=False):
        if chroot == None:
            return self.run_script(key, chroot=self.settings["path/work"], optional=optional)
        else:
            return self.run_script(key, chroot=chroot, optional=optional)

    def __init__(self, settings):
        target.__init__(self, settings)

        # DEFINE GENERAL LINUX CHROOT MOUNTS

        self.mounts = ["/proc"]
        self.mountmap = {"/proc":"/proc" }

        # CCACHE SUPPORT FOR CHROOTS

        if not self.settings.has_key("metro/class"):
            return

        skey = "metro/options/"+self.settings["metro/class"]

        # enable ccache and pkgcache support - all we do in python is bind-mount the right directory to the right place.

        for key, name, dest in [
                [ "path/cache/compiler", "cache/compiler", "/var/tmp/cache/compiler" ] ,
                [ "path/cache/package", "cache/package", "/var/tmp/cache/package" ] ,
                [ "path/cache/probe", "probe", "/var/tmp/cache/probe" ] ]:
            if self.settings.has_key(skey) and name in self.settings[skey].split():
                if not self.settings.has_key(key):
                    raise MetroError, "Required setting %s not found (for %s option support)" % ( key, name )
                if not os.path.exists(self.settings[key]):
                    os.makedirs(self.settings[key])
                self.mounts.append(dest)
                self.mountmap[dest] = self.settings[key]

    def bind(self):
        """ Perform bind mounts """
        for mount in self.mounts:
            if not os.path.exists(self.settings["path/work"]+mount):
                os.makedirs(self.settings["path/work"]+mount, 0755)

            if not os.path.exists(self.mountmap[mount]):
                os.makedirs(self.mountmap[mount], 0755)

            src = self.mountmap[mount]
            print "Mounting %s to %s..." % (src, mount)
            if os.system(CMDS["mount"]+" --bind "+src+" "+self.settings["path/work"]+mount) != 0:
                self.unbind()
                raise MetroError, "Couldn't bind mount "+src

    def unbind(self, attempt=0):
        mounts = self.get_active_mounts()
        while len(mounts) != 0:
            # now, go through our dictionary and try to unmound
            progress = 0
            mpos = 0
            while mpos < len(mounts):
                self.cmd("umount "+mounts[mpos], badval=10)
                if not ismount(mounts[mpos]):
                    del mounts[mpos]
                    progress += 1
                else:
                    mpos += 1
            if progress == 0:
                break

        mounts = self.get_active_mounts()
        if len(mounts):
            if attempt >= 3:
                mstring = ""
                for mount in mounts:
                    mstring += mount+"\n"
                raise MetroError, "The following bind mounts could not be unmounted: \n"+mstring
            else:
                attempt += 1
                self.kill_chroot_pids()
                self.unbind(attempt=attempt)

    def get_active_mounts(self):
        # os.path.realpath should ensure that we are comparing the right thing, if something in the path
        # is a symlink - like /var/tmp -> /foo. Because /proc/mounts will store the resolved path (ie.
        # /foo/metro) not the regular one (ie. /var/tmp/metro)
        prefix = os.path.realpath(self.settings["path/work"])
        # this used to have a "os.popen("mount")" which is not as accurate as the kernel list /proc/mounts.
        # The "mount" command relies on /etc/mtab which is not necessarily correct.
        myf = open("/proc/mounts","r")
        mylines = myf.readlines()
        myf.close()
        outlist = []
        for line in mylines:
            mypath = line.split()[1]
            if mypath[0:len(prefix)] == prefix:
                outlist.append(mypath)
        return outlist

    def check_mounts(self):
        mymounts = self.get_active_mounts()
        if len(mymounts) == 0:
            return
        else:
            self.unbind()

    def run(self, required_files=None):
        if self.target_exists("path/mirror/target"):
            self.run_script("trigger/ok/run", optional=False)
            return

        # look for required files
        for loc in [ "path/mirror/source" ] + (required_files or []):
            try:
                matches = glob(self.settings[loc])
            except:
                raise MetroError, "Setting %s is set to %s; glob failed." % ( loc, repr(self.settings[loc]) )
            if len(matches) == 0:
                raise MetroError, "Required file "+self.settings[loc]+" not found. Aborting."
            elif len(matches) > 1:
                raise MetroError, "Multiple matches found for required file pattern defined in '%s'; Aborting." % loc

        # BEFORE WE CLEAN UP - MAKE SURE WE ARE UNMOUNTED
        self.kill_chroot_pids()
        self.check_mounts()

        # BEFORE WE START - CLEAN UP ANY MESSES
        self.clean_path(recreate=True)
        try:
            self.check_mounts()
            self.run_script("steps/unpack")
            self.run_script("steps/unpack/post", optional=True)

            self.bind()

            self.run_script_in_chroot("steps/chroot/prerun", optional=True)
            self.run_script_in_chroot("steps/chroot/run")
            self.run_script_in_chroot("steps/chroot/postrun", optional=True)

            self.unbind()

            self.run_script_in_chroot("steps/chroot/clean", optional=True)
            self.run_script_in_chroot("steps/chroot/test", optional=True)
            self.run_script_in_chroot("steps/chroot/postclean", optional=True)
        except:
            self.kill_chroot_pids()
            self.check_mounts()
            raise

        self.run_script("steps/capture")
        self.run_script("trigger/ok/run", optional=True)

        self.kill_chroot_pids()
        self.check_mounts()
        self.clean_path()

class snapshot(target):
    def __init__(self, settings):
        target.__init__(self, settings)

    def run(self):
        if self.target_exists("path/mirror/snapshot"):
            self.run_script("trigger/ok/run", optional=True)
            return

        target.run(self)

class stage(chroot):

    def __init__(self, settings):
        chroot.__init__(self, settings)

        # DEFINE GENTOO MOUNTS
        if self.settings.has_key("path/distfiles"):
            self.mounts.append("/usr/portage/distfiles")
            self.mountmap["/usr/portage/distfiles"] = self.settings["path/distfiles"]

        # let's bind-mount our main system's device nodes in place
        if self.settings["portage/ROOT"] != "/":
            # this seems to be needed for libperl to build (x2p) during stage1 - so we'll mount it....
            self.mounts.append("/dev")
            self.mounts.append("/dev/pts")
            self.mountmap["/dev"] = "/dev"
            self.mountmap["/dev/pts"] = "/dev/pts"

    def run(self):
        chroot.run(self, ["path/mirror/snapshot"])

        # Now, we want to clean up our build-related caches, if configured to do so:
        if self.settings.has_key("metro/options"):
            if "clean/auto" in self.settings["metro/options"].split():
                if self.settings.has_key("path/cache/build"):
                    self.clean_path(self.settings["path/cache/build"])

# vim: ts=4 sw=4 et
