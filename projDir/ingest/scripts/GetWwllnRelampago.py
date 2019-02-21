#!/usr/bin/env python

#===========================================================================
#
# Download ltg files from web site using http
#
#===========================================================================

import os
import sys
import time
import datetime
from datetime import timedelta
import string
import subprocess
from optparse import OptionParser
import httplib
import base64

def main():

    global options

    # parse the command line

    parseArgs()

    # initialize
    
    beginString = "BEGIN: GetWwllnRelampago.py"
    today = datetime.datetime.now()
    beginString += " at " + str(today)
    
    if (options.force == True):
        beginString += " (get forced)"

    print "==========================================================="
    print beginString
    print "==========================================================="

    # create tmp dir if necessary

    if not os.path.exists(options.tmpDir):
        runCommand("mkdir -p " + options.tmpDir)

    # open http connection
    
    conn = httplib.HTTPConnection(options.httpServer)
    auth = base64.b64encode(options.httpUser + ":" + options.httpPassword)
    headers = { "Authorization" : "Basic %s" % auth }

    if (options.verbose == True):
        print >>sys.stderr, 'auth =', auth
        print >>sys.stderr, "headers = ", headers
    
    # grab the page listing available file:
    
    conn.request("GET", options.sourceDir, "", headers)
    response = conn.getresponse()
    if (options.debug == True):
        print >>sys.stderr, "====>> response status, reason", response.status, response.reason
    if (int(response.status) != 200):
        print >>sys.stderr, "ERROR reading index.html"
        sys.exit(1)
        
    lines = response.read().split('\n')

    # look through the lines, finding the file names
    # compile file list

    fileList = []
    for line in lines:
        if (options.verbose == True):
            print >>sys.stderr, "http line: ", line
        nameLoc = line.find("RelampagoWWLLN.loc")
        if (nameLoc > 0):
            nameStart = nameLoc - 14;
            fileName = line[nameStart:nameStart + 32]
            fileList.append(fileName)
            # if (options.verbose == True):
            #     print >>sys.stderr, "-->> found fileName: ", fileName

    if (options.verbose == True):
        for fileName in fileList:
            print >>sys.stderr, "-->> found fileName: ", fileName

    # get current time

    nowTime = time.gmtime()
    now = datetime.datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
                            nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
    nowTimeStr = now.strftime("%Y%m%d%H%M%S")

    # compute start time

    pastSecs = timedelta(0, int(options.pastSecs))
    startTime = now - pastSecs
    startTimeStr = startTime.strftime("%Y%m%d%H%M%S")

    if (options.debug == True):
        print >>sys.stderr, "  time now: ", nowTimeStr
        print >>sys.stderr, "  getting data after: ", startTimeStr

    # go through files in list

    count = 0
    for fileName in fileList:
        
        if (options.verbose == True):
            print >>sys.stderr, "  remoteName: ", fileName

        # check name against substring list if needed
        
        if (checkFileName(fileName) == False):
            continue

        if (options.verbose == True):
            print >>sys.stderr, "  valid name: ", fileName

        # process this file
            
        dateStr = fileName[1:9]
        dateTimeStr = fileName[1:13]
        if (options.verbose == True):
            print >>sys.stderr, "  dateStr: ", dateStr
            print >>sys.stderr, "  dateTimeStr: ", dateTimeStr

        startTimeVal = int(startTimeStr)
        fileTimeVal = int(dateTimeStr) * 100

        if (options.verbose == True):
            print >>sys.stderr, "  startTimeVal: ", startTimeVal
            print >>sys.stderr, "   fileTimeVal: ", fileTimeVal

        if (fileTimeVal >= startTimeVal):
        
            dayDir = os.path.join(options.targetDir, dateStr)
            if (options.verbose == True):
                print >>sys.stderr, "dayDir: ", dayDir

            # create day dir if necessary
            
            if not os.path.exists(dayDir):
                runCommand("mkdir -p " + dayDir)

            # check if file has already been retrieved
            
            fileAlreadyHere = False
            for root, dirs, localfiles in os.walk(dayDir):
                for localName in localfiles:
                    if (localName == fileName):
                        fileAlreadyHere = True

            if (options.verbose == True):
                print >>sys.stderr, "fileAlreadyHere: ", fileAlreadyHere
                            
            if ((fileAlreadyHere == False) or (options.force == True)):

                # read file using http

                print "====>> Getting file: ", fileName

                conn.request("GET", options.sourceDir + fileName, "", headers)
                response = conn.getresponse()
                if (options.debug == True):
                    print >>sys.stderr, "====>> response status, reason",\
                          response.status, response.reason

                if (int(response.status) != 200):
                    print >>sys.stderr, "ERROR reading file: ", fileName
                    continue

                # store in tmp
                
                tmpPath = os.path.join(options.tmpDir, fileName)
                if (options.verbose == True):
                    print >>sys.stderr, "retrieving file, storing as tmpPath: ", tmpPath
                    
                tmpFile = open(tmpPath, 'w')
                tmpFile.write(response.read())
                tmpFile.close()
                
                # move to final location

                cmd = "mv " + tmpPath + " " + dayDir
                runCommand(cmd)
                finalPath = os.path.join(dayDir, fileName)
                print >>sys.stderr, "Renamed to final path: ", finalPath

                # write latest_data_info
                
                relPath = os.path.join(dateStr, fileName)
                cmd = "LdataWriter -dir " + options.targetDir \
                      + " -rpath " + relPath \
                      + " -ltime " + str(fileTimeVal) \
                      + " -writer getLtgDataByHttp.py" \
                      + " -dtype txt"
                runCommand(cmd)

                count += 1

    if (count == 0):
        print "---->> No files to  download"
        
    print "=========================================================================="
    print "END: GetWwllnRelampago.pyy at " + str(datetime.datetime.now())
    print "=========================================================================="

    sys.exit(0)


########################################################################
# Parse the command line

def parseArgs():
    
    global options

    # parse the command line

    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option('--debug',
                      dest='debug', default='False',
                      action="store_true",
                      help='Set debugging on')
    parser.add_option('--verbose',
                      dest='verbose', default='False',
                      action="store_true",
                      help='Set verbose debugging on')
    parser.add_option('--force',
                      dest='force', default='False',
                      action="store_true",
                      help='Force http transfer')
    parser.add_option('--httpServer',
                      dest='httpServer',
                      default='wwlln.net',
                      help='Name of http server host')
    parser.add_option('--httpUser',
                      dest='httpUser',
                      default='relampago',
                      help='User for http authorization')
    parser.add_option('--httpPassword',
                      dest='httpPassword',
                      default='BrodzikWWLLN',
                      help='Password for http authorization')
    parser.add_option('--sourceDir',
                      dest='sourceDir',
                      default='/relampago/',
                      help='Path of source directory')
    defaultTargetDir = os.path.join(os.getenv("DATA_DIR"), "relampago/raw/wwlln")
    parser.add_option('--targetDir',
                      dest='targetDir',
                      default=defaultTargetDir,
                      help='Path of target directory')
    parser.add_option('--tmpDir',
                      dest='tmpDir',
                      default="/tmp/data/raw/wwlln",
                      help='Path of tmp directory')
    parser.add_option('--pastSecs',
                      dest='pastSecs',
                      default=7200,
                      help='How far back to retrieve (secs)')
    parser.add_option('--checkNames',
                      dest='checkNames', default='False',
                      action="store_true",
                      help='Check that the file name contains one of the substrings ' +
                      'defined by the --subStrList option. ' +
                      'Each remote file will be checked against the list of strings and ' +
                      'will only be downloaded if a match is found.')
    parser.add_option('--subStrList',
                      dest='subStrList',
                      default=".loc",
                      help='Define the list of substrings against which the remote ' 
                      'filenames will be checked. This is a comma-delimited list. ' +
                      ' The default list is: ".loc"')

    (options, args) = parser.parse_args()

    if (options.verbose == True):
        options.debug = True

    if (options.debug == True):
        print >>sys.stderr, "Options:"
        print >>sys.stderr, "  debug? ", options.debug
        print >>sys.stderr, "  force? ", options.force
        print >>sys.stderr, "  httpServer: ", options.httpServer
        print >>sys.stderr, "  sourceDir: ", options.sourceDir
        print >>sys.stderr, "  tmpDir: ", options.tmpDir
        print >>sys.stderr, "  pastSecs: ", options.pastSecs

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
# Check file name against list of substrings

def checkFileName(fileName):

    if (options.checkNames == False):
        return True

    subStrList = string.split(options.subStrList, ',')
    found = False

    for subStr in subStrList:

        if (fileName.find(subStr) >= 0):
            if (options.verbose == True):
                print "  -->> subStr '" + subStr + "' matches"
                print "       fileName: ", fileName
            return True

    # substring match not found
    # don't process this file

    if (options.verbose == True):
        print "  -->> fileName does not match subStrings: ", fileName
        print "       subStringList: '", options.subStrList, "'"

    return False

########################################################################
# kick off main method

if __name__ == "__main__":

   main()
