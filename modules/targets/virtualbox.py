import os, sys, time, types, glob
import subprocess

from catalyst_support import MetroError, ismount

from .remote import RemoteTarget

class VirtualboxTarget(RemoteTarget):
    def __init__(self, settings):
        RemoteTarget.__init__(self, settings)

        # virtualbox specifics
        self.required_files.append("path/mirror/generator")
        self.basedir = self.settings["path/work"]+"/vm"

        self.cmds["modprobe"] = "/sbin/modprobe"
        self.cmds["vbox"] = "/usr/bin/VBoxManage"

        self.ssh_uri = "root@10.99.99.2"
        self.remote_upload_path = "/tmp"

        if self.settings["target/arch"] == "amd64":
            self.ostype = "Gentoo_64"
        else:
            self.ostype = "Gentoo"

    def prepare_remote(self):
        if self.settings["target/arch"] not in ["amd64", "x86"]:
            raise MetroError, "VirtualBox target class only supports x86 targets"

        for mod in ["vboxdrv", "vboxpci", "vboxnetadp", "vboxnetflt"]:
            self.cmd(self.cmds["modprobe"]+" "+mod)

        self.ssh_key_path = self.settings["path/config"]+"/keys/vagrant"

    def clean_remote(self):
        pass

    def start_remote(self):
        # create vm
        self.vbm("createvm --name %s --ostype %s --basefolder '%s' --register" % (self.name, self.ostype, self.basedir))
        self.vbm("modifyvm %s --rtcuseutc on --boot1 disk --boot2 dvd --boot3 none --boot4 none" % (self.name))
        self.vbm("modifyvm %s --memory %s" % (self.name, self.settings["virtualbox/memory"]))
        self.vbm("modifyvm %s --vrde on --vrdeport 3389 --vrdeauthtype null" % (self.name))

        # create hard drive
        self.vbm("createhd --filename '%s/%s.vdi' --size $((%s*1024)) --format vdi" % (self.basedir, self.name, self.settings["virtualbox/hddsize"]))
        self.vbm("storagectl %s --name 'SATA Controller' --add sata --controller IntelAhci --bootable on --sataportcount 2" % (self.name))
        self.vbm("storageattach %s --storagectl 'SATA Controller' --type hdd --port 0 --medium '%s/%s.vdi'" % (self.name, self.basedir, self.name))

        # attach generator
        self.vbm("storageattach %s --storagectl 'SATA Controller' --type dvddrive --port 1 --medium '%s'" % (self.name, self.settings["path/mirror/generator"]))

        # create hostonly network
        ifcmd = self.cmds["vbox"]+" hostonlyif create 2>/dev/null | /bin/egrep -o 'vboxnet[0-9]+'"
        self.ifname = subprocess.check_output(ifcmd, shell=True).strip()
        self.vbm("hostonlyif ipconfig %s --ip 10.99.99.1" % (self.ifname,))
        self.cmd("ip link set %s up" % (self.ifname,))

        # setup vm networking
        self.vbm("modifyvm %s --nic1 nat --nic2 hostonly" % (self.name))
        self.vbm("modifyvm %s --hostonlyadapter2 %s" % (self.name, self.ifname))

        # start the vm
        self.vbm("startvm %s --type headless" % (self.name))

        # 60 seconds should be enough to boot
        # a better heuristic would be nice though
        time.sleep(60)

    def wait_for_shutdown(self):
        sys.stdout.write("Waiting for VM to shutdown .")
        check_cmd = self.cmds["vbox"]+" list runningvms | /bin/fgrep -o "+self.name

        while True:
            sys.stdout.write(".")
            try:
                subprocess.check_output(check_cmd, shell=True)
            except subprocess.CalledProcessError:
                sys.stdout.write(" done\n")
                break
            time.sleep(1)

        time.sleep(60)

    def capture(self):
        self.run_script("steps/capture")

    def destroy_remote(self):
        try:
            self.vbm("controlvm %s poweroff && sleep 5" % (self.name))
        except:
            pass

        # determine virtual network if we don't have it
        if not hasattr(self, "ifname"):
            ifcmd = self.cmds["vbox"]+" list hostonlyifs|grep -B3 10.99.99.1|head -n1|awk '{print $2}'"
            self.ifname = subprocess.check_output(ifcmd, shell=True).strip()

        try:
            self.vbm("unregistervm %s --delete" % (self.name))
        except:
            pass

        try:
            self.vbm("hostonlyif remove %s" % (self.ifname))
        except:
            pass

    def vbm(self, cmd):
        self.cmd(self.cmds["vbox"]+" "+cmd)

# vim: ts=4 sw=4 et
