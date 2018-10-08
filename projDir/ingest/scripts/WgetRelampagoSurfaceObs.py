#!/usr/bin/env python

#===========================================================================
#
# Wget the surface obs for Relampago
# These are csv text files
#
#===========================================================================

import os
import sys
import subprocess
from optparse import OptionParser
import math
import time
import datetime
from datetime import timedelta

def main():

    # globals

    global options
    global debug
    global startTime
    global endTime
    global timeLimitsSet
    timeLimitsSet = False
    global figNum
    figNum = 0

    # parse the command line

    usage = "usage: " + __file__ + " [options]"
    parser = OptionParser(usage)
    parser.add_option('--debug',
                      dest='debug', default=False,
                      action="store_true",
                      help='Set debugging on')
    parser.add_option('--verbose',
                      dest='verbose', default=False,
                      action="store_true",
                      help='Set verbose debugging on')
    parser.add_option('--url',
                      dest='url',
                      default='http://cimaps.cima.fcen.uba.ar/relampago/estaciones',
                      help='URL of data download location')
    parser.add_option('--outDir',
                      dest='outDir',
                      default='/scr/hail1/rsfdata/relampago/raw/surface_obs',
                      help='Output directory. Day dirs are below this.')
    
    (options, args) = parser.parse_args()
    
    if (options.verbose == True):
        options.debug = True

    # compute day string for today
    
    now = time.gmtime()
    nowTime = datetime.datetime(now.tm_year, now.tm_mon, now.tm_mday,
                                now.tm_hour, now.tm_min, now.tm_sec)
    todayStr = nowTime.strftime("%Y%m%d")
    todayUrlStr = nowTime.strftime("%Y/%m/%d")

    # compute day string for yesterday
    
    oneDay = timedelta(0, 86400)
    yesterdayTime = nowTime - oneDay
    yesterdayStr = yesterdayTime.strftime("%Y%m%d")
    yesterdayUrlStr = yesterdayTime.strftime("%Y/%m/%d")
    
    # create urls and output dirs

    todayUrl = os.path.join(options.url, todayUrlStr)
    yesterdayUrl = os.path.join(options.url, yesterdayUrlStr)

    todayOutDir = os.path.join(options.outDir, todayStr)
    yesterdayOutDir = os.path.join(options.outDir, yesterdayStr)

    # debug
    
    if (options.debug):
        print >>sys.stderr, "Running ", __file__
        print >>sys.stderr, "  url: ", options.url
        print >>sys.stderr, "  todayUrlStr: ", todayUrlStr
        print >>sys.stderr, "  yesterdayUrlStr: ", yesterdayUrlStr
        print >>sys.stderr, "  todayUrl: ", todayUrl
        print >>sys.stderr, "  yesterdayUrl: ", yesterdayUrl
        print >>sys.stderr, "  todayOutDir: ", todayOutDir
        print >>sys.stderr, "  yesterdayOutDir: ", yesterdayOutDir

    # make directories

    if not os.path.exists(todayOutDir):
        try:
            os.makedirs(todayOutDir)    
        except Exception as e:
            print("ERROR - cannot make dir: " , todayOutDir)  
            print("  exception: " , e)  
            sys.exit(1)

    if not os.path.exists(yesterdayOutDir):
        try:
            os.makedirs(yesterdayOutDir)    
        except Exception as e:
            print("ERROR - cannot make dir: " , yesterdayOutDir)  
            print("  exception: " , e)  
            sys.exit(1)

    # run wget

    if (now.tm_hour < 3):
        os.chdir(yesterdayOutDir)
        cmd = 'wget -m -nd --accept "*.csv" -e robots=off --level=1 ' + yesterdayUrl
        runCommand(cmd)
    
    os.chdir(todayOutDir)
    cmd = 'wget -m -nd --accept "*.csv" -e robots=off --level=1 ' + todayUrl
    runCommand(cmd)

    sys.exit(0)
    
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

