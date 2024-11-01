#!/usr/bin/env python

#=====================================================================
#
# Download RMA radar files from ftp site
#
#=====================================================================

import os
import sys
import time
import datetime
from datetime import timedelta
import string
import ftplib
import subprocess
from optparse import OptionParser

def main():

    global options
    global ftpUser
    global ftpPassword
    global ftpDebugLevel
    global tmpDir
    global startTime, endTime
    global count
    count = 0

    global thisScriptName
    thisScriptName = os.path.basename(__file__)

    # parse the command line

    parseArgs()

    # initialize
    
    beginString = "BEGIN: " + thisScriptName
    today = datetime.datetime.now()
    beginString += " at " + str(today)
    
    if (options.force):
        beginString += " (ftp forced)"

    print "\n========================================================"
    print beginString
    print "========================================================="

    # create tmp dir if necessary

    try:
        os.makedirs(options.tmpDir)
    except OSError as exc:
        if (options.verbose):
            print >>sys.stderr, "WARNING: cannot make tmp dir: ", options.tmpDir
            print >>sys.stderr, "  ", exc
            
    # set ftp debug level

    if (options.verbose):
        ftpDebugLevel = 2
    elif (options.debug):
        ftpDebugLevel = 1
    else:
        ftpDebugLevel = 0
    
    # get current date and time

    nowTime = time.gmtime()
    now = datetime.datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
                            nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
    nowDateStr = now.strftime("%Y%m%d")
    nowDateTimeStr = now.strftime("%Y%m%d%H%M%S")

    # compute time strings

    startDateTimeStr = startTime.strftime("%Y%m%d%H%M%S")
    startDateStr = startTime.strftime("%Y%m%d")
    endDateTimeStr = endTime.strftime("%Y%m%d%H%M%S")
    endDateStr = endTime.strftime("%Y%m%d")

    # set up list of days to be checked

    timeInterval = endTime - startTime
    if (options.debug):
        print >>sys.stderr, "  startTime: ", startTime
        print >>sys.stderr, "  endTime: ", endTime
        print >>sys.stderr, "  timeInterval: ", timeInterval
        print >>sys.stderr, "  nDays: ", timeInterval.days

    # loop through the hours

    thisTime = startTime
    while (thisTime <= endTime):
        if (options.debug):
            print >>sys.stderr, "  thisTime: ", thisTime
        thisTime = thisTime + timedelta(0, 3600, 0)
        try:
            getDataForHour(thisTime)
        except:
            print >>sys.stderr, "FTP failed"
        
    if (count == 0):
        print "---->> No files to download"
        
    print "==============================================================="
    print "END: " + thisScriptName + str(datetime.datetime.now())
    print "==============================================================="

    sys.exit(0)

########################################################################
# Get the data for a specified hour

def getDataForHour(dataTime):

    global count

    if (options.debug):
        print >>sys.stderr, "====>> getting data for time: ", dataTime
        print >>sys.stderr, "  year: ", dataTime.year
        print >>sys.stderr, "  month: ", dataTime.month
        print >>sys.stderr, "  day: ", dataTime.day
        print >>sys.stderr, "  hour: ", dataTime.hour

    # make the target directory and go there
    
    dateStr = dataTime.strftime("%Y%m%d")
    timeStr = dataTime.strftime("%Y%m%d%H%M%S")
    localDayDir = os.path.join(options.targetDir, dateStr)
    try:
        os.makedirs(localDayDir)
    except OSError as exc:
        if (options.verbose):
            print >>sys.stderr, "WARNING: trying to create dir: ", localDayDir
            print >>sys.stderr, "  ", exc
    os.chdir(localDayDir)

    # get local file list - i.e. those which have already been downloaded
    
    localFileList = os.listdir('.')
    localFileList.reverse()
    if (options.verbose):
        print >>sys.stderr, "  localFileList: ", localFileList
            
    # open ftp connection
    
    ftp = ftplib.FTP(options.ftpServer, options.ftpUser, options.ftpPasswd)
    ftp.set_debuglevel(ftpDebugLevel)

    # got to source directory on the ftp site

    hourStr = dataTime.strftime("%Y/%m/%d/%H")
    hourDir = options.sourceDir + "/" + hourStr

    if (options.debug):
        print >>sys.stderr, "====>> cd to hourDir: ", hourDir

    ftp.cwd(hourDir)

    # get list of volume times in this hour

    hourDirList = ftp.nlst()
    if (options.debug):
        print >>sys.stderr, "====>> times in this hour: ", dataTime
    
    # loop through the vol times

    for volTimeStr in hourDirList:
        
        # go there

        volDir = hourDir + "/" + volTimeStr

        if (options.debug):
            print >>sys.stderr, "  volTimeStr: ", volTimeStr
            print >>sys.stderr, "  volDir: ", volDir

        ftp.cwd(volDir)

        # get list of files

        fileList = ftp.nlst()

        # loop through file list, getting the BUFR files

        for fileName in fileList:
            if (fileName.find('BUFR') > 0):
                if (fileName not in localFileList):
                    downloadFile(ftp, dateStr, timeStr, fileName)
                    count = count + 1

    # close ftp connection
    
    ftp.quit()

########################################################################
# Download a file into the current directory

def downloadFile(ftp, dateStr, timeStr, fileName):
    
    if (options.debug):
        print >>sys.stderr, "  downloading file: ", fileName
        
    # get file, store in tmp

    tmpPath = os.path.join(options.tmpDir, fileName)

    if (options.verbose):
        print >>sys.stderr, "retrieving file, storing as tmpPath: ", tmpPath
    ftp.retrbinary('RETR '+ fileName, open(tmpPath, 'wb').write)

    # move to final location - i.e. this directory
    
    cmd = "mv " + tmpPath + " ."
    runCommand(cmd)

    # write latest_data_info
    
    relPath = os.path.join(dateStr, fileName)
    cmd = "LdataWriter -dir " + options.targetDir \
          + " -rpath " + relPath \
          + " -ltime " + timeStr \
          + " -writer " + thisScriptName \
          + " -dtype bufr"
    runCommand(cmd)

########################################################################
# Parse the command line

def parseArgs():
    
    global options
    global startTime, endTime

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
    parser.add_option('--force',
                      dest='force', default=False,
                      action="store_true",
                      help='Force ftp transfer')
    parser.add_option('--ftpServer',
                      dest='ftpServer',
                      default='200.16.116.24',
                      help='Name of ftp server host')
    parser.add_option('--ftpUser',
                      dest='ftpUser',
                      default='Lvidal',
                      help='User for ftp host')
    parser.add_option('--ftpPasswd',
                      dest='ftpPasswd',
                      default='lv1d4l',
                      help='Passwd for ftp host')
    parser.add_option('--sourceDir',
                      dest='sourceDir',
                      default='/L2/RMA1',
                      help='Path of source directory')
    parser.add_option('--targetDir',
                      dest='targetDir',
                      default='/home/relamp/projDir/data/relampago/raw/radar/catchup/RMA1',
                      help='Path of target directory')
    parser.add_option('--tmpDir',
                      dest='tmpDir',
                      default='/tmp/radar/RMA1',
                      help='Path of tmp directory')
    parser.add_option('--start',
                      dest='startTime',
                      default='1970 01 01 00 00 00',
                      help='Start time for retrieval')
    parser.add_option('--end',
                      dest='endTime',
                      default='1970 01 01 00 00 00',
                      help='End time for retrieval')

    (options, args) = parser.parse_args()

    if (options.verbose):
        options.debug = True

    syear, smonth, sday, shour, sminute, ssec = options.startTime.split()
    startTime = datetime.datetime(int(syear), int(smonth), int(sday),
                                  int(shour), int(sminute), int(ssec))

    eyear, emonth, eday, ehour, eminute, esec = options.endTime.split()
    endTime = datetime.datetime(int(eyear), int(emonth), int(eday),
                                int(ehour), int(eminute), int(esec))

    # check if start/end time is set?

    if (syear == '1970' and eyear == '1970'):

        # get current date and time
        
        now = time.gmtime()
        nowTime = datetime.datetime(now.tm_year, now.tm_mon, now.tm_mday,
                                    now.tm_hour, now.tm_min, now.tm_sec)
        
        # start time is 2 days before now
        # end time is 2 days before now
        
        startTime = nowTime - timedelta(2, 0, 0)
        endTime = nowTime + timedelta(2, 0, 0)

    if (options.debug):
        print >>sys.stderr, "Options:"
        print >>sys.stderr, "  debug? ", options.debug
        print >>sys.stderr, "  force? ", options.force
        print >>sys.stderr, "  ftpServer: ", options.ftpServer
        print >>sys.stderr, "  ftpUser: ", options.ftpUser
        print >>sys.stderr, "  sourceDir: ", options.sourceDir
        print >>sys.stderr, "  targetDir: ", options.targetDir
        print >>sys.stderr, "  tmpDir: ", options.tmpDir
        print >>sys.stderr, "  startTime: ", startTime
        print >>sys.stderr, "  endTime: ", endTime

########################################################################
# Run a command in a shell, wait for it to complete

def runCommand(cmd):

    if (options.debug):
        print >>sys.stderr, "running cmd:",cmd
    
    try:
        retcode = subprocess.call(cmd, shell=True)
        if retcode < 0:
            print >>sys.stderr, "Child was terminated by signal: ", -retcode
        else:
            if (options.debug):
                print >>sys.stderr, "Child returned code: ", retcode
    except OSError, e:
        print >>sys.stderr, "Execution failed:", e

########################################################################
# kick off main method

if __name__ == "__main__":

   main()
