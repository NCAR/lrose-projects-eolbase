#!/usr/bin/env python

#================================================================
#
# check CfRadial files for time coverage etc.
#
#================================================================

from __future__ import print_function

import os
import sys
import time
import datetime
from datetime import timedelta
import string
import subprocess
from optparse import OptionParser

def main():

    global options
    global startTime
    global endTime
    global sumFileDuration
    global appName
    appName = os.path.basename(__file__)
    sumFileDuration = timedelta(0)

    # parse the command line

    parseArgs()

    # go to the directory

    if (os.path.exists(options.dirPath) == False):
        print("ERROR - ", appName)
        print("  dir does not exist: ", options.dirPath)
        sys.exit(1)

    os.chdir(options.dirPath)
    if (options.debug == True):
        print("working on dir: ", options.dirPath)

    # get listing of dated dirs
    
    dirList = os.listdir(options.dirPath)

    for dir in dirList:

        if (options.debug):
            print("  checking dir: ", dir)

        try:

            # get date
            yearStr = dir[0:4]
            monthStr = dir[4:6]
            dayStr = dir[6:]

            # compute dir start time
            dirStartTime = datetime.datetime(int(yearStr), int(monthStr), int(dayStr),
                                             0, 0, 0)
            if (options.debug):
                print("  dirStartTime: ", dirStartTime, file=sys.stderr)
            if (dirStartTime < startTime):
                if (options.verbose):
                    print("  dir time before start time: ", dir, file=sys.stderr)
                continue

            # compute dir end time
            dirEndTime = datetime.datetime(int(yearStr), int(monthStr), int(dayStr),
                                           23, 59, 59)
            if (options.debug):
                print("  dirEndTime: ", dirEndTime, file=sys.stderr)
            if (dirEndTime > endTime):
                if (options.verbose):
                    print("  dir time after end time: ", dir, file=sys.stderr)
                continue

        except Exception as e:
            if (options.debug):
                print("  Ignoring dir: ", dir, file=sys.stderr)
                print("  exception: ", e, file=sys.stderr)

        if (options.debug):
            print("  accepting dir: ", dir, file=sys.stderr)
        subDirPath = os.path.join(options.dirPath, dir)
        if (os.path.isdir(subDirPath)):
            processDir(subDirPath)

    print("====>>>> sumfileDuration: ", sumFileDuration, file=sys.stderr)

    sys.exit(0)

#############################################
# process a dated subdirectory

def processDir(subDirPath):

    # go to the subdir

    if (options.debug):
        print("working on subdir: ", subDirPath)

    # get a listing

    os.chdir(subDirPath)
    fileList = os.listdir(subDirPath)

    # create the links

    for fileName in fileList:
        try:
            processFileName(fileName)
        except Exception as e:
            print("  bad file name: ", fileName, file=sys.stderr)
            print("  dir: ", subDirPath, file=sys.stderr)
            print("  exception: ", e, file=sys.stderr)

    return

#############################################
# process a file name

def processFileName(fileName):

    # get file start time

    startYear = fileName[6:10]
    startMonth = fileName[10:12]
    startDay = fileName[12:14]
    startHour = fileName[15:17]
    startMin = fileName[17:19]
    startSec = fileName[19:21]

    endYear = fileName[29:33]
    endMonth = fileName[33:35]
    endDay = fileName[35:37]
    endHour = fileName[38:40]
    endMin = fileName[40:42]
    endSec = fileName[42:44]
    
    fileStartTime = datetime.datetime(int(startYear), int(startMonth), int(startDay),
                                      int(startHour), int(startMin), int(startSec))
    if (options.verbose):
        print("  fileStartTime: ", fileStartTime, file=sys.stderr)
    if (fileStartTime < startTime):
        if (options.verbose):
            print("  file time before start time: ", fileName, file=sys.stderr)
        return
        
    fileEndTime = datetime.datetime(int(endYear), int(endMonth), int(endDay),
                                    int(endHour), int(endMin), int(endSec))
    if (options.verbose):
        print("  fileEndTime: ", fileEndTime, file=sys.stderr)
    if (fileEndTime > endTime):
        if (options.verbose):
            print("  file time after end time: ", fileName, file=sys.stderr)
        return

    fileDuration = fileEndTime - fileStartTime
    if (options.debug):
        print("  file name, duration: ", fileName, fileDuration, file=sys.stderr)
        
    global sumFileDuration
    sumFileDuration = sumFileDuration + fileDuration

    return

######################################################
# Parse the command line

def parseArgs():
    
    global options
    global startTime
    global endTime

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
                      help='Set verbose debuggin on')
    parser.add_option('--dirPath',
                      dest='dirPath',
                      default='/scr/hail1/rsfdata/eolbase/cfradial/spol/moments/sband/sur',
                      help='Path to directory')
    parser.add_option('--start',
                      dest='startTime',
                      default='2017 10 15 00 00 00',
                      help='Start time for analysis')
    parser.add_option('--end',
                      dest='endTime',
                      default='2018 05 30 00 00 00',
                      help='End time for analysis')

    (options, args) = parser.parse_args()

    if (options.verbose):
        options.debug = True

    year, month, day, hour, minute, sec = options.startTime.split()
    startTime = datetime.datetime(int(year), int(month), int(day),
                                  int(hour), int(minute), int(sec))

    year, month, day, hour, minute, sec = options.endTime.split()
    endTime = datetime.datetime(int(year), int(month), int(day),
                                int(hour), int(minute), int(sec))

    if (options.debug):
        print("Running app: ", appName, file=sys.stderr)
        print("Options:", file=sys.stderr)
        print("  debug: ", options.debug, file=sys.stderr)
        print("  verbose: ", options.verbose, file=sys.stderr)
        print("  dirPath: ", options.dirPath, file=sys.stderr)
        print("  startTime: ", startTime, file=sys.stderr)
        print("  endTime: ", endTime, file=sys.stderr)

################################################################
# Run a command in a shell, wait for it to complete

def runCommand(cmd):

    if (options.debug == True):
        print("running cmd:",cmd, file=sys.stderr)
    
    try:
        retcode = subprocess.call(cmd, shell=True)
        if retcode < 0:
            print("Child was terminated by signal: ", -retcode, file=sys.stderr)
        else:
            if (options.debug == True):
                print("Child returned code: ", retcode, file=sys.stderr)
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)

###########################################################
# kick off main method

if __name__ == "__main__":

   main()
