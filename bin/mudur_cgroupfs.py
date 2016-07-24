# -*- coding : utf-8 -*-
import os, sys

def mountpoint(path):
    status = os.system("mountpoint -q %s" % path)
    if status == 0:
        return True
    else:
        return False

class Controller:
    def __init__(self, subsysname, hierarchy, num_cgroups, enabled ):
        self.subsysname = subsysname
        self.hierarchy = hierarchy
        self.num_cgroups = num_cgroups
        self.enabled = enabled

    def mount(self):
        if self.enabled == 1:
            os.chdir("/sys/fs/cgroup")
            if mountpoint(self.subsysname) == False:
                s = self.subsysname
                status = os.system("mkdir -p %s; mount -n -t cgroup -o %s cgroup %s" % (s, s,s))
                if status == 0:
                    return True
                else:
                    return False


class Cgroupfs:
    def __init__(self):
        self.controllers = {}
        if self.check_fstab == True:
            print("cgroupfs in fstab, exiting.")
            sys.exit(-1)

        if self.kernel_support() == False:
            print("No kernel support for cgroupfs, exiting.")
            sys.exit(-2)

        if self.check_sysfs() == False:
            print("/sys/fs/cgroups directory not found, exiting")
            sys.exit(-3)

        self.mount_cgroup()
        self.find_controllers()
        for cname, c in self.controllers.items():
            c.mount()

    def check_fstab(self):
        found = False
        for line in open("/etc/fstab").readlines():
            if line[0] == "#":
                continue
            else:
                if line.find("cgroup"):
                    found = True
        return found

    def kernel_support(self):
        return os.path.isfile("/proc/cgroups")

    def check_sysfs(self):
        return  os.path.isdir("/sys/fs/cgroup")

    def mount_cgroup(self):
        if mountpoint("/sys/fs/cgroup") == False:
            cmd = " mount -t tmpfs -o uid=0,gid=0,mode=0755 cgroup /sys/fs/cgroup"
            return  os.system(cmd)

    def find_controllers(self):
        for line in open("/proc/cgroups").readlines():
            line = line.strip()
            if line[0] == "#":
                continue
            else:
                subsysname, hierarchy, num_cgroups, enabled = line.split()
                enb = int(enabled)
                hie = int(hierarchy)
                numc= int(num_cgroups)
                self.controllers[subsysname] = Controller(subsysname, hie, numc, enb)
