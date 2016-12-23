#!/usr/bin/env python

#===========================================================================
#
# Produce plots for clutter monitor analysis
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
    parser.add_option('--cm_file',
                      dest='cmFilePath',
                      default='../data/pecan/clut_mon.txt',
                      help='ClutMon results file path')
    parser.add_option('--cp_file',
                      dest='cpFilePath',
                      default='../data/pecan/spol_pecan_CP_analysis_20150524_000021.txt',
                      help='CP results file path')
    parser.add_option('--title',
                      dest='title',
                      default='CLUTTER MONITORING ANALYSIS',
                      help='Title for plot')
    parser.add_option('--width',
                      dest='figWidthMm',
                      default=400,
                      help='Width of figure in mm')
    parser.add_option('--height',
                      dest='figHeightMm',
                      default=320,
                      help='Height of figure in mm')
    parser.add_option('--lenMean',
                      dest='lenMean',
                      default=1,
                      help='Len of moving mean filter')
    
    (options, args) = parser.parse_args()
    
    if (options.verbose == True):
        options.debug = True

    if (options.debug == True):
        print >>sys.stderr, "Running %prog"
        print >>sys.stderr, "  cmFilePath: ", options.cmFilePath
        print >>sys.stderr, "  cpFilePath: ", options.cpFilePath

    # read in column headers for self_con results

    iret, cmHdrs, cmData = readColumnHeaders(options.cmFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for self_con results

    cmData, cmTimes = readInputData(options.cmFilePath, cmHdrs, cmData)

    # read in column headers for CP results

    iret, cpHdrs, cpData = readColumnHeaders(options.cpFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for CP results

    cpData, cpTimes = readInputData(options.cpFilePath, cpHdrs, cpData)

    # render the plot
    
    doPlot(cmData, cmTimes, cpData, cpTimes)

    sys.exit(0)
    
########################################################################
# Read columm headers for the data
# this is in the first line

def readColumnHeaders(filePath):

    colHeaders = []
    colData = {}

    fp = open(filePath, 'r')
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
        return -1, colHeaders, colData
    
    for index, var in enumerate(colHeaders, start=0):
        colData[var] = []
        
    return 0, colHeaders, colData

########################################################################
# Read in the data

def readInputData(filePath, colHeaders, colData):

    # open file

    fp = open(filePath, 'r')
    lines = fp.readlines()

    # read in a line at a time, set colData
    for line in lines:
        
        commentIndex = line.find("#")
        if (commentIndex >= 0):
            continue
            
        # data
        
        data = line.strip().split()

        for index, var in enumerate(colHeaders, start=0):
            if (var == 'count' or var == 'obsNum' or \
                var == 'year' or var == 'month' or var == 'day' or \
                var == 'hour' or var == 'min' or var == 'sec' or \
                var == 'nDbzStrong' or var == 'nDbmhcStrong' or \
                var == 'nDbmvcStrong' or var == 'nDbmhxStrong' or \
                var == 'nDbmvxStrong' or var == 'nZdrStrong' or \
                var == 'nXpolrStrong' or \
                var == 'nDbzWeak' or var == 'nDbmhcWeak' or \
                var == 'nDbmvcWeak' or var == 'nDbmhxWeak' or \
                var == 'nDbmvxWeak' or var == 'nZdrWeak' or \
                var == 'nXpolrWeak' or \
                var == 'unix_time'):
                colData[var].append(int(data[index]))
            elif (var == 'fileName' or var == 'volTime'):
                colData[var].append(data[index])
            else:
                colData[var].append(float(data[index]))

    fp.close()

    # load observation times array

    year = colData['year']
    month = colData['month']
    day = colData['day']
    hour = colData['hour']
    minute = colData['min']
    sec = colData['sec']

    obsTimes = []
    for ii, var in enumerate(year, start=0):
        thisTime = datetime.datetime(year[ii], month[ii], day[ii],
                                     hour[ii], minute[ii], sec[ii])
        obsTimes.append(thisTime)

    return colData, obsTimes

########################################################################
# Moving average filter

def movingAverage(values, window):

    weights = np.repeat(1.0, window)/window
    sma = np.convolve(values, weights, 'same')
    return sma

########################################################################
# Plot

def doPlot(cmData, cmTimes, cpData, cpTimes):

    # running filter

    lenMeanFilter = int(options.lenMean)
    
    # times
    
    cmtimes = np.array(cmTimes).astype(datetime.datetime)

    # set up plot structure

    widthIn = float(options.figWidthMm) / 25.4
    htIn = float(options.figHeightMm) / 25.4

    fig1 = plt.figure(1, (widthIn, htIn))
    ax1 = fig1.add_subplot(3,1,1,xmargin=0.0)
    ax2 = fig1.add_subplot(3,1,2,xmargin=0.0)
    ax3 = fig1.add_subplot(3,1,3,xmargin=0.0)

    ax1.plot(cmTimes, np.zeros(len(cmTimes)), linewidth=1, color = 'gray')
    ax2.plot(cmTimes, np.zeros(len(cmTimes)), linewidth=1, color = 'gray')
    ax3.plot(cmTimes, np.zeros(len(cmTimes)), linewidth=1, color = 'gray')

    ax1.set_xlim([cmtimes[0], cmtimes[-1]])
    ax2.set_xlim([cmtimes[0], cmtimes[-1]])
    ax3.set_xlim([cmtimes[0], cmtimes[-1]])
    
    fileName = options.cmFilePath
    titleStr = "File: " + fileName
    hfmt = dates.DateFormatter('%y/%m/%d')

    # weather contamination

    fractionWxWeak = np.array(cmData["fractionWxWeak"]).astype(np.double)
    wxContam = np.array(cmData["wxContamination"]).astype(np.double)
    # noWx = (wxContam < 1)
    noWx = (fractionWxWeak < 0.15)
    timesNoWx = cmtimes[noWx]

    # HC power - axis 1

    dbmhcStrong = np.array(cmData["meanDbmhcStrong"]).astype(np.double)
    dbmhcStrong = movingAverage(dbmhcStrong, lenMeanFilter)
    validDbmhcStrong = np.isfinite(dbmhcStrong)

    ax1.plot(cmtimes[validDbmhcStrong], dbmhcStrong[validDbmhcStrong], \
             label = 'DBMHC strong', linewidth=1, color='orange')
    
    dbmhcNoWx = dbmhcStrong[noWx]
    (dbmhcTimes, dbmhcMeans, dbmhcPerc) = computeDailyStats(timesNoWx, dbmhcNoWx)

    # VC power - axis 1
    
    dbmvcStrong = np.array(cmData["meanDbmvcStrong"]).astype(np.double)
    dbmvcStrong = movingAverage(dbmvcStrong, lenMeanFilter)
    validDbmvcStrong = np.isfinite(dbmvcStrong)
    
    ax1.plot(cmtimes[validDbmvcStrong], dbmvcStrong[validDbmvcStrong], \
             label = 'DBMVC strong', linewidth=1, color='cyan')

    dbmvcNoWx = dbmvcStrong[noWx]
    (dbmvcTimes, dbmvcMeans, dbmvcPerc) = computeDailyStats(timesNoWx, dbmvcNoWx)

    # daily means

    ax1.plot(dbmhcTimes, dbmhcMeans, \
             linewidth=2, label = 'DBMHC daily mean', color = 'red')
    ax1.plot(dbmhcTimes, dbmhcMeans, "^", color = 'red', markersize=9)

    ax1.plot(dbmvcTimes, dbmvcMeans, \
             linewidth=2, label = 'DBMVC daily mean', color = 'blue')
    ax1.plot(dbmvcTimes, dbmvcMeans, "^", color = 'blue', markersize=9)

    # ZDR from strong clutter - axis 2
    
    zdrStrong = np.array(cmData["meanZdrStrong"]).astype(np.double)
    zdrStrong = movingAverage(zdrStrong, lenMeanFilter)
    validZdrStrong = np.isfinite(zdrStrong)

    ax2.plot(cmtimes[validZdrStrong], zdrStrong[validZdrStrong], \
             label = 'ZDR strong clutter', linewidth=1, color='red')

    zdrNoWx = zdrStrong[noWx]
    (zdrTimes, zdrMeans, zdrPerc) = computeDailyStats(timesNoWx, zdrNoWx)
    ax2.plot(zdrTimes, zdrMeans, \
             linewidth=2, label = 'ZDR daily mean (dB)', color = 'black')
    ax2.plot(zdrTimes, zdrMeans, \
             "k^", color = 'black', markersize=9)

    # cross polar power ratio - axis 2

    xpolrStrong = np.array(cmData["meanXpolrStrong"]).astype(np.double)
    xpolrStrong = movingAverage(xpolrStrong, lenMeanFilter)
    validXpolrStrong = np.isfinite(xpolrStrong)

    ax2.plot(cmtimes[validXpolrStrong], xpolrStrong[validXpolrStrong], \
             label = 'XPOLR strong clutter', linewidth=1, color='green')

    validFraction = np.isfinite(fractionWxWeak)
    ax2.plot(cmtimes[validFraction], fractionWxWeak[validFraction], \
             label = 'Weather fraction weak', linewidth=1, color='purple')

    ax2.plot(cmtimes[noWx], fractionWxWeak[noWx], \
             "o", label = 'No wx', color='purple', markersize=2)
    
    # transmit power - axis 3

    cptimes = np.array(cpTimes).astype(datetime.datetime)
    timeStart1us = datetime.datetime(2015, 6, 8, 0, 0, 0)
    pwrCorrFlag = cptimes < timeStart1us
    pwrCorr = np.zeros(len(cptimes))
    pwrCorr[cptimes < timeStart1us] = -1.76

    TxPwrH = np.array(cpData["TxPwrH"]).astype(np.double)
    TxPwrH = movingAverage(TxPwrH, lenMeanFilter)
    TxPwrH = TxPwrH + pwrCorr
    validTxPwrH = np.isfinite(TxPwrH)

    TxPwrV = np.array(cpData["TxPwrV"]).astype(np.double)
    TxPwrV = movingAverage(TxPwrV, lenMeanFilter)
    TxPwrV = TxPwrV + pwrCorr
    validTxPwrV = np.isfinite(TxPwrV)

    ax3.plot(cptimes[validTxPwrH], TxPwrH[validTxPwrH], \
             label = 'TxPwrH', linewidth=1, color='blue')

    ax3.plot(cptimes[validTxPwrV], TxPwrV[validTxPwrV], \
             label = 'TxPwrV', linewidth=1, color='cyan')

    # legends etc
    
    configureAxis(ax1, -20.0, 0.0, "Clutter power strong/weak (dBm)")
    configureAxis(ax2, -2.5, 1.5, "Wx fraction and ZDR (dB/fraction)")
    configureAxis(ax3, 87, 87.8, "Measured Xmit power (dBm)")

    fig1.suptitle("SPOL PECAN CLUTTER MONITORING ANALYSIS")
    fig1.autofmt_xdate()

    plt.tight_layout()
    plt.subplots_adjust(top=0.96)
    plt.show()

########################################################################
# initialize legends etc

def configureAxis(ax, miny, maxy, ylabel):
    
    legend = ax.legend(loc='upper right', ncol=6)
    for label in legend.get_texts():
        label.set_fontsize('x-small')
    ax.set_xlabel("Date")
    ax.set_ylabel(ylabel)
    ax.grid(True)
    if (miny > -9990 and maxy > -9990):
        ax.set_ylim([miny, maxy])
    hfmt = dates.DateFormatter('%y/%m/%d')
    ax.xaxis.set_major_locator(dates.DayLocator())
    ax.xaxis.set_major_formatter(hfmt)
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(8) 

########################################################################
# compute daily means for dbz bias

def computeDailyStats(times, vals):

    dailyTimes = []
    dailyMeans = []
    dailyPercs = []

    nptimes = np.array(times).astype(datetime.datetime)
    npvals = np.array(vals).astype(np.double)

    validFlag = np.isfinite(npvals)
    timesValid = nptimes[validFlag]
    valsValid = npvals[validFlag]
    
    startTime = nptimes[0]
    endTime = nptimes[-1]
    
    startDate = datetime.datetime(startTime.year, startTime.month, startTime.day, 0, 0, 0)
    endDate = datetime.datetime(endTime.year, endTime.month, endTime.day, 0, 0, 0)

    oneDay = datetime.timedelta(1)
    halfDay = datetime.timedelta(0.5)
    
    thisDate = startDate
    while (thisDate < endDate + oneDay):
        
        nextDate = thisDate + oneDay
        result = []
        
        sum = 0.0
        sumDeltaTime = datetime.timedelta(0)
        count = 0.0
        for ii, val in enumerate(valsValid, start=0):
            thisTime = timesValid[ii]
            if (thisTime >= thisDate and thisTime < nextDate):
                # only use times before 10 UTC (late afternoon and night hours)
                if (thisTime.hour > 10):
                    continue
                sum = sum + val
                deltaTime = thisTime - thisDate
                sumDeltaTime = sumDeltaTime + deltaTime
                count = count + 1
                result.append(val)
        if (count > 1):
            mean = sum / count
            meanDeltaTime = datetime.timedelta(0, sumDeltaTime.total_seconds() / count)
            dailyMeans.append(mean)
            dailyTimes.append(thisDate + meanDeltaTime)
            # print >>sys.stderr, " daily time, meanStrong: ", dailyTimes[-1], meanStrong
            result.sort()
            dailyPercs.append(result[len(result)/5])
            
        thisDate = thisDate + oneDay

    return (dailyTimes, dailyMeans, dailyPercs)


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

