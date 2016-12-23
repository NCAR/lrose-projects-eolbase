#!/usr/bin/env python

#===========================================================================
#
# Create links from files to fortran units, for CEDRIC - ARCHIVE MODE
#
#===========================================================================

import os
import sys
from stat import *
import time
import datetime
from datetime import timedelta
import string
import subprocess
from optparse import OptionParser
import math

def main():

    global options

    # parse the command line

    parseArgs()

    # start message

    runPath = __file__
    if (options.debug == True):
        print >>sys.stderr, "==================================================================="
        print >>sys.stderr, \
            "START: " + runPath + " at " + str(datetime.datetime.now())
        print >>sys.stderr, "==================================================================="

    # compute full path of data
    
    radarDir = os.path.join(options.cartDataDir, options.radarName);

    if (options.debug == True):
        print >>sys.stderr, "  radarDir: ", radarDir

    # change dir to where links are required

    os.chdir(options.cartDataDir);

    # remove link if it already exists

    cmd = "/bin/rm -f " + options.linkName
    runCommand(cmd)

    # get the path to the closest data file in time, within the specified margin

    dataFilePath = getDataFilePath(radarDir)
    if (len(dataFilePath) < 1):
        print >>sys.stderr, "  No file found within specified time margin"
        sys.exit(1)

    if (options.debug == True):
        print >>sys.stderr, "  dataFilePath: ", dataFilePath

    # create link

    cmd = "ln -s " + dataFilePath + " " + options.linkName
    runCommand(cmd)

    sys.exit(0)

########################################################################
# Parse the command line

def parseArgs():
    
    global options

    # parse the command line

    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option('--debug',
                      dest='debug', default=False,
                      action="store_true",
                      help='Set debugging on')
    parser.add_option('--verbose',
                      dest='verbose', default=False,
                      action="store_true",
                      help='Set verbose debugging on')
    parser.add_option('--time',
                      dest='time',
                      default='2015 06 25 23 00 00',
                      help='Time for which links will be created')
    parser.add_option('--margin',
                      dest='marginSecs',
                      default=600,
                      help='Time margin when searching for links (secs)')
    parser.add_option('--cart_data_dir',
                      dest='cartDataDir',
                      default='/scr/hail2/rsfdata/pecan/cedric/multidop',
                      help='Directory for Cartesian input data')
    parser.add_option('--radar_name',
                      dest='radarName',
                      default='unknown',
                      help='Name of radar')
    parser.add_option('--link_name',
                      dest='linkName',
                      default='fort.00',
                      help='Name of fortran link')

    (options, args) = parser.parse_args()

    if (options.debug == True):
        print >>sys.stderr, "Options:"
        print >>sys.stderr, "  debug? ", options.debug
        print >>sys.stderr, "  verbose? ", options.verbose
        print >>sys.stderr, "  time: ", options.time
        print >>sys.stderr, "  marginSecs: ", options.marginSecs
        print >>sys.stderr, "  cartDataDir: ", options.cartDataDir
        print >>sys.stderr, "  radarName: ", options.radarName
        print >>sys.stderr, "  linkName: ", options.linkName

########################################################################
# get the path to the closest data file in time, within the specified margin

def getDataFilePath(radarDir):

    # requested time

    (year, month, day, hour, minute, sec) = options.time.split()
    timeRequested = datetime.datetime(int(year), int(month), int(day),
                                      int(hour), int(minute), int(sec))
    if (options.debug):
        print >>sys.stderr, "  timeRequested: ", timeRequested

    # get list of day dirs in radar dir

    dayDirs = os.listdir(radarDir)
    dayDirs.sort()
    searchDirs = []
    for dayDir in dayDirs:
        if (len(dayDir) != 8):
            continue
        dayYear = int(dayDir[0:4])
        dayMonth = int(dayDir[4:6])
        dayDay = int(dayDir[6:8])
        if (dayYear < 2000 or dayYear > 2100 or
            dayMonth < 1 or dayMonth > 12 or
            dayDay < 1 or dayDay > 31):
            continue
        midDay = datetime.datetime(dayYear, dayMonth, dayDay, 12, 0, 0)
        deltaSecs = (midDay - timeRequested).total_seconds()
        absDelta = math.fabs(deltaSecs)
        if (absDelta < 86400):
            searchDirs.append(dayDir)

    if (options.debug):
        print >>sys.stderr, "  searchDirs: ", searchDirs

    minDeltaSecs = options.marginSecs + 1
    dataFilePath = ""
    for searchDir in searchDirs:
        searchPath = os.path.join(radarDir, searchDir)
        fileNames = os.listdir(searchPath)
        fileNames.sort()
        for fileName in fileNames:
            parts = fileName.split('_')
            if (len(parts) < 3 or len(parts[1]) != 8 or len(parts[2]) != 6):
                continue
            fyear = int(parts[1][0:4])
            fmonth = int(parts[1][4:6])
            fday = int(parts[1][6:8])
            fhour = int(parts[2][0:2])
            fmin = int(parts[2][2:4])
            fsec = int(parts[2][4:6])
            ftime = datetime.datetime(fyear, fmonth, fday, fhour, fmin, fsec)
            fDeltaSecs = math.fabs((ftime - timeRequested).total_seconds())
            if (fDeltaSecs > options.marginSecs):
                continue
            if (options.debug):
                print >>sys.stderr, "    searchPath: ", searchPath
                print >>sys.stderr, "    fileName: ", fileName
                print >>sys.stderr, "    ftime: ", ftime
                print >>sys.stderr, "    fDeltaSecs: ", fDeltaSecs
            if (fDeltaSecs < minDeltaSecs):
                dataFilePath = os.path.join(searchPath, fileName)
                minDeltaSecs = fDeltaSecs

    return dataFilePath

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
# kick off main method

if __name__ == "__main__":

   main()
