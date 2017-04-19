#!/usr/bin/env python

#===========================================================================
#
# Delete files smaller than a specified size from the current directory
#
#===========================================================================

from __future__ import print_function

import os
import sys
import subprocess
from optparse import OptionParser
import numpy as np
from numpy import convolve
import math
import datetime

def main():

#   globals

    global options
    global debug
    appName = os.path.basename(__file__)

# parse the command line

    usage = "usage: " + appName + " [options]"
    parser = OptionParser(usage)
    parser.add_option('--debug',
                      dest='debug', default=False,
                      action="store_true",
                      help='Set debugging on')
    parser.add_option('--verbose',
                      dest='verbose', default=False,
                      action="store_true",
                      help='Set verbose debugging on')
    parser.add_option('--dir',
                      dest='dirPath',
                      default='.',
                      help='Directory to clean up')
    parser.add_option('--minSize',
                      dest='minSize',
                      default=0,
                      help='Size of smallest valid file in bytes')
    
    (options, args) = parser.parse_args()
    
    if (options.verbose == True):
        options.debug = True

    if (options.debug == True):
        print("Running script: ", appName, file=sys.stderr)
        print("  dir: ", options.dirPath, file=sys.stderr)
        print("  minSize: ", options.minSize, file=sys.stderr)

    # perform the cleanup
    
    doCleanup(options.dirPath, int(options.minSize))

    sys.exit(0)
    
########################################################################
# Perform the cleanup

def doCleanup(dir, minFileSize):

    fileList = os.listdir(dir)

    print("Filelist:\n", fileList, file=sys.stderr)

    for fileName in fileList:
        filePath = os.path.join(dir, fileName)
        if (os.path.isfile(filePath)):
            fileSize = int(os.path.getsize(filePath))
            print("FilePath, size: ", filePath, ", ", fileSize, file=sys.stderr)
            if (fileSize < minFileSize):
                print("===>> DELETING file: ", filePath, file=sys.stderr)
                os.remove(filePath)

########################################################################
# Run a command in a shell, wait for it to complete

def runCommand(cmd):

    if (options.debug == True):
        print >>sys.stderr, "running cmd:",cmd
    
    try:
        retcode = subprocess.call(cmd, shell=True)
        if retcode < 0:
            print >>sys.stderr, "Child was terminated by signal: ", -retcode
        else:
            if (options.debug == True):
                print >>sys.stderr, "Child returned code: ", retcode
    except OSError, e:
        print >>sys.stderr, "Execution failed:", e

########################################################################
# Run - entry point

if __name__ == "__main__":
   main()

