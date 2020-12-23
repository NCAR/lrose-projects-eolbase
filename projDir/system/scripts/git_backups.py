#!/usr/bin/env python

#===========================================================================
#
# Check out lrose git repos every day, as a backup
#
# Use --help to see the command line options.
#
#===========================================================================

from __future__ import print_function
import os
import sys
import shutil
import subprocess
from optparse import OptionParser
import time
from datetime import datetime
from datetime import date
from datetime import timedelta
import glob

def main():

    # globals

    global thisScriptName
    thisScriptName = os.path.basename(__file__)

    global thisScriptDir
    thisScriptDir = os.path.dirname(__file__)

    global options
    
    # parse the command line
    
    usage = "usage: " + thisScriptName + " [options]"
    homeDir = os.environ['HOME']
    targetDirDefault = os.path.join(homeDir, 'backups4git')
    parser = OptionParser(usage)
    parser.add_option('--debug',
                      dest='debug', default=True,
                      action="store_true",
                      help='Set debugging on')
    parser.add_option('--targetDir',
                      dest='targetDir', default=targetDirDefault,
                      help='Target dir, default is $HOME/backups4git')

    (options, args) = parser.parse_args()
    
    # runtime

    now = time.gmtime()
    nowTime = datetime(now.tm_year, now.tm_mon, now.tm_mday,
                       now.tm_hour, now.tm_min, now.tm_sec)
    dateStr = nowTime.strftime("%Y%m%d")

    # make date dir and go there

    dateDir = os.path.join(options.targetDir, dateStr);
    if (os.path.isdir(dateDir) == False):
        os.makedirs(dateDir)
    os.chdir(dateDir)

    # set up repo list
    
    repos = []
    repos.append("git@github.com:ncar/lrose-core")
    repos.append("git@github.com:ncar/CfRadial")
    repos.append("git@github.com:ncar/HCR_instrument")
    repos.append("git@github.com:ncar/hsrl_configuration")
    repos.append("git@github.com:ncar/hsrl_instrument")
    repos.append("git@github.com:ncar/ka-band_instrument")
    repos.append("git@github.com:ncar/lrose-cedric")
    repos.append("git@github.com:ncar/lrose-devel")
    repos.append("git@github.com:ncar/lrose-displays")
    repos.append("git@github.com:ncar/lrose-docs")
    repos.append("git@github.com:ncar/lrose-eumetsat")
    repos.append("git@github.com:ncar/lrose-examples")
    repos.append("git@github.com:ncar/lrose-hurricane-lane")
    repos.append("git@github.com:ncar/lrose-lucid")
    repos.append("git@github.com:ncar/lrose-ncms")
    repos.append("git@github.com:ncar/lrose-netcdf")
    repos.append("git@github.com:ncar/lrose-pound")
    repos.append("git@github.com:ncar/lrose-projects-eolbase")
    repos.append("git@github.com:ncar/lrose-projects-lakevic")
    repos.append("git@github.com:ncar/lrose-projects-relampago")
    repos.append("git@github.com:ncar/lrose-solo3")
    repos.append("git@github.com:ncar/lrose-soloii")
    repos.append("git@github.com:ncar/lrose-sysview")
    repos.append("git@github.com:ncar/lrose-test")
    repos.append("git@github.com:ncar/lrose-titan")
    repos.append("git@github.com:ncar/spol-configuration")
    repos.append("git@github.com:ncar/spol-control")
    repos.append("git@github.com:ncar/spol-instrument")
    repos.append("git@github.com:ncar/spoldrx")
    repos.append("git@github.com:ncar/titan-cswr")
    repos.append("git@github.com:ncar/titan-dowdrx")
    repos.append("git@github.com:ncar/titan-java")
    repos.append("git@github.com:ncar/titan-legacy")
    repos.append("git@github.com:ncar/titan-templates")
    repos.append("git@github.com:ncar/titan-web")
    repos.append("git@github.com:ncar/xpol-configuration")

    repos.append("git@github.com:ncar/apar")

    repos.append("git@github.com:mmbell/fractl")
    repos.append("git@github.com:mmbell/samurai")
    repos.append("git@github.com:mmbell/vortrac")

    for repo in repos:
        gitCheckout(repo)

    sys.exit(0)

########################################################################
# check out repos from git

def gitCheckout(repoUrl):

    parts = repoUrl.split("/")
    repoName = parts[len(parts) - 1]
    
    if (os.path.isdir(repoName)):
        print("repo already checkout out, ignoring:", repoName, file=sys.stderr)
        return
    
    print("checking out repo:", repoUrl, file=sys.stderr)
    shellCmd("git clone " + repoUrl)

########################################################################
# Run a command in a shell, wait for it to complete

def shellCmd(cmd):

    print("Running cmd:", cmd, file=sys.stderr)
    
    try:
        retcode = subprocess.check_call(cmd, shell=True)
        if retcode != 0:
            print("Child exited with code: ", retcode, file=sys.stderr)
            sys.exit(1)
        else:
            if (options.debug):
                print("Child returned code: ", retcode, file=sys.stderr)
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)
        sys.exit(1)

    print("    done", file=sys.stderr)
    
########################################################################
# Run - entry point

if __name__ == "__main__":
   main()
