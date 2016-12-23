#!/usr/bin/env python

#===========================================================================
#
# Save SPOL ambient temp to SPDB
#
#===========================================================================

import os
import sys
import subprocess
from optparse import OptionParser
import numpy as np
from numpy import convolve
import matplotlib.pyplot as plt
from matplotlib import dates
import math
import datetime

def main():

#   globals

    global options
    global debug
    
    global colHeaders
    colHeaders = []

    global colIndex
    colIndex = {}
    
    global colData
    colData = {}

    global obsTimes
    obsTimes = []

    projDir = os.environ['PROJ_DIR']

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
    parser.add_option('--file',
                      dest='inputFilePath',
                      default = projDir + '/cal/data/pecan/spol_dish_amb_gps_temps.txt',
                      help='Input file path')
    parser.add_option('--url',
                      dest='spdbUrl',
                      default='spdbp:://hail:0:pecan/spdb/spol/temps',
                      help='Output SPDB url')
    
    (options, args) = parser.parse_args()

    print >>sys.stderr, "options: ", options
    
    if (options.verbose == True):
        options.debug = True

    if (options.debug == True):
        print >>sys.stderr, "Running SpolAmbientTemp2Spdb:"
        print >>sys.stderr, "  inputFilePath: ", options.inputFilePath
        print >>sys.stderr, "  outputUrl: ", options.spdbUrl

    # read in column headers

    if (readColumnHeaders() != 0):
        sys.exit(-1)

    # read in file

    readInputData()

    # write to SPDB
    
    writeToSpdb()

    sys.exit(0)
    
########################################################################
# Read columm headers for the data
# this is in the fist line

def readColumnHeaders():

    global colHeaders
    global colIndex
    global colData

    fp = open(options.inputFilePath, 'r')
    line = fp.readline()
    fp.close()
    
    commentIndex = line.find("#")
    if (commentIndex == 0):
        # header
        colHeaders = line.lstrip("# ").rstrip("\n").split()
        if (options.debug == True):
            print >>sys.stderr, "colHeaders: ", colHeaders
    else:
        print >>sys.stderr, "ERROR - readColumnHeaders"
        print >>sys.stderr, "  First line does not start with #"
        return -1
    
    for index, var in enumerate(colHeaders, start=0):
        colIndex[var] = index
        colData[var] = []
        
    if (options.debug == True):
        print >>sys.stderr, "colIndex: ", colIndex

    return 0

########################################################################
# Read in the data

def readInputData():

    global colData
    global obsTimes

    # open file

    fp = open(options.inputFilePath, 'r')
    lines = fp.readlines()

    # read in a line at a time, set colData
    for line in lines:
        
        commentIndex = line.find("#")
        if (commentIndex >= 0):
            continue
            
        # data
        
        data = line.strip().split()

        for index, var in enumerate(colHeaders, start=0):
            colData[var].append(data[index])

    fp.close()

########################################################################
# write data to spdb

def writeToSpdb():

    # load column arrays

    yyyymmddhhmmss = colData['yyyymmddhhmmss']
    dishTemp = colData['DishTempC']
    outsideTemp = colData['OutsideTempC']
    gpsTemp = colData['GPSTempC']
    obsTimes = []

    for ii, var in enumerate(yyyymmddhhmmss, start=0):

        year = yyyymmddhhmmss[ii][0:4]
        month = yyyymmddhhmmss[ii][4:6]
        day = yyyymmddhhmmss[ii][6:8]
        hour = yyyymmddhhmmss[ii][8:10]
        min = yyyymmddhhmmss[ii][10:12]
        sec = yyyymmddhhmmss[ii][12:14]
        thisTime = datetime.datetime(int(year), int(month), int(day),
                                     int(hour), int(min), int(sec))
        obsTimes.append(thisTime)

        outsideTemp = float(colData['OutsideTempC'][ii])
        dishTemp = float(colData['DishTempC'][ii])
        gpsTemp = float(colData['GPSTempC'][ii])

        temp = outsideTemp
        if (temp < -99):
            temp = dishTemp
        if (temp < -99):
            temp = gpsTemp

        if (options.debug == True):
            print >>sys.stderr, "time, outside, dish, gps, used:", \
                thisTime, ", ", outsideTemp, ", ", dishTemp, ", ", gpsTemp, ", ", temp

        cmd = 'SpdbXmlPut -url ' + options.spdbUrl + ' ' + \
              '-datatype SPOL ' + \
              '-spdb_id 101 ' + \
              '-spdb_label "Mesonet Station Report Data" ' + \
              '-expire_secs 600 -outer_tag weather_observation ' + \
              '-tag temp_c -val ' + str(temp) + ' ' + \
              '-tag station_id -val SPOL ' + \
              '-tag long_name -val "NCAR SPOL radar at PECAN" ' + \
              '-tag latitude -val 38.553164 ' + \
              '-tag longitude -val -99.535739 ' + \
              '-tag elevation_m -val 667.0 ' + \
              '-tag observation_time -val ' + \
              year + '-' + month + '-' + day + 'T' + \
              hour + ':' + min + ':' + sec + ' ' + \
              '-valid "' + \
              year + ' ' + month + ' ' + day + ' ' + \
              hour + ' ' + min + ' ' + sec + '"'

        runCommand(cmd)

    return

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

