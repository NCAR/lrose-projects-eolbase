#!/usr/bin/env python

#===========================================================================
#
# Produce plots for field diffs from original to QC
#
#===========================================================================

import os
import sys
import subprocess
from optparse import OptionParser
import numpy as np
from numpy import convolve
from numpy import linalg, array, ones
import matplotlib.pyplot as plt
from matplotlib import dates
import math
import datetime
import contextlib

def main():

#   globals

    global options
    global debug
    global startTime
    global endTime

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
    parser.add_option('--diffs_file',
                      dest='diffsFilePath',
                      default='../data/pecan/field_diffs.spol.qc.txt',
                      help='File path for bias results')
    parser.add_option('--cp_file',
                      dest='cpFilePath',
                      default='../data/pecan/cp_analysis.spol.txt',
                      help='CP results file path')
    parser.add_option('--title',
                      dest='title',
                      default='FIELD DIFFS - ORIGINAL TO QC',
                      help='Title for plot')
    parser.add_option('--width',
                      dest='figWidthMm',
                      default=400,
                      help='Width of figure in mm')
    parser.add_option('--height',
                      dest='figHeightMm',
                      default=200,
                      help='Height of figure in mm')
    parser.add_option('--lenMean',
                      dest='lenMean',
                      default=1,
                      help='Len of moving mean filter')
    parser.add_option('--start',
                      dest='startTime',
                      default='1970 01 01 00 00 00',
                      help='Start time for XY plot')
    parser.add_option('--end',
                      dest='endTime',
                      default='1970 01 01 01 00 00',
                      help='End time for XY plot')
    
    (options, args) = parser.parse_args()
    
    if (options.verbose == True):
        options.debug = True

    year, month, day, hour, minute, sec = options.startTime.split()
    startTime = datetime.datetime(int(year), int(month), int(day),
                                  int(hour), int(minute), int(sec))

    year, month, day, hour, minute, sec = options.endTime.split()
    endTime = datetime.datetime(int(year), int(month), int(day),
                                int(hour), int(minute), int(sec))

    if (options.debug == True):
        print >>sys.stderr, "Running %prog"
        print >>sys.stderr, "  cpFilePath: ", options.cpFilePath
        print >>sys.stderr, "  diffsFilePath: ", options.diffsFilePath
        print >>sys.stderr, "  startTime: ", startTime
        print >>sys.stderr, "  endTime: ", endTime

    # read in column headers for diffs results

    iret, diffsHdrs, diffsData = readColumnHeaders(options.diffsFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for diffs results

    diffsData, diffsTimes = readInputData(options.diffsFilePath, diffsHdrs, diffsData)

    # read in column headers for CP results

    iret, cpHdrs, cpData = readColumnHeaders(options.cpFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for CP results

    cpData, cpTimes = readInputData(options.cpFilePath, cpHdrs, cpData)

    # render the plot
    
    doPlot(diffsData, diffsTimes, cpData, cpTimes)

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
            if (var == 'count' or var == 'year' or var == 'month' or var == 'day' or \
                var == 'hour' or var == 'min' or var == 'sec' or \
                var == 'unix_time'):
                colData[var].append(int(data[index]))
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

    if (window < 2):
        return values

    weights = np.repeat(1.0, window)/window
    sma = np.convolve(values, weights, 'same')
    return sma

########################################################################
# Plot

def doPlot(diffsData, diffsTimes, cpData, cpTimes):

    fileName = options.diffsFilePath
    titleStr = "File: " + fileName
    hfmt = dates.DateFormatter('%y/%m/%d')

    lenMeanFilter = int(options.lenMean)

    # set up arrays for diffs

    dtimes = np.array(diffsTimes).astype(datetime.datetime)
    
    dbzDiffs = np.array(diffsData["DBZ_F_diffMean"]).astype(np.double)
    dbzDiffs = movingAverage(dbzDiffs, lenMeanFilter)
    dbzValid = np.isfinite(dbzDiffs)
    
    zdrDiffs = np.array(diffsData["ZDR_F_diffMean"]).astype(np.double)
    zdrDiffs = movingAverage(zdrDiffs, lenMeanFilter)
    zdrValid = np.isfinite(zdrDiffs)
    
    validDbzDtimes = dtimes[dbzValid]
    validDbzVals = dbzDiffs[dbzValid]
    
    validZdrDtimes = dtimes[zdrValid]
    validZdrVals = zdrDiffs[zdrValid]
    
    # load up receiver gain etc - axis 4
    
    (dailyTimeDbz, dailyValDbz) = computeDailyStats(validDbzDtimes, validDbzVals)
    (dailyTimeZdr, dailyValZdr) = computeDailyStats(validZdrDtimes, validZdrVals)

    # transmit power

    cptimes = np.array(cpTimes).astype(datetime.datetime)

    timeStart1us = datetime.datetime(2015, 6, 8, 0, 0, 0)
    pwrCorrFlag = cptimes < timeStart1us
    pwrCorr = np.zeros(len(cptimes))
    pwrCorr[cptimes < timeStart1us] = -1.76
    
    TxPwrH = np.array(cpData["TxPwrH"]).astype(np.double)
    TxPwrH = movingAverage(TxPwrH, 11)
    TxPwrH = TxPwrH + pwrCorr
    validTxPwrH = np.isfinite(TxPwrH)

    TxPwrV = np.array(cpData["TxPwrV"]).astype(np.double)
    TxPwrV = movingAverage(TxPwrV, 11)
    TxPwrV = TxPwrV + pwrCorr
    validTxPwrV = np.isfinite(TxPwrV)

    # set up plots

    widthIn = float(options.figWidthMm) / 25.4
    htIn = float(options.figHeightMm) / 25.4

    fig1 = plt.figure(1, (widthIn, htIn))

    ax1a = fig1.add_subplot(2,1,1,xmargin=0.0)
    ax1b = fig1.add_subplot(2,1,2,xmargin=0.0)
    #ax1c = fig1.add_subplot(3,1,3,xmargin=0.0)

    oneDay = datetime.timedelta(1.0)
    ax1a.set_xlim([dtimes[0] - oneDay, dtimes[-1] + oneDay])
    ax1a.set_title("DBZ and ZDR differences, QC minus original (dB)")
    ax1b.set_xlim([dtimes[0] - oneDay, dtimes[-1] + oneDay])
    ax1b.set_title("Daily mean differences, QC minus original (dB)")
    #ax1c.set_xlim([dtimes[0] - oneDay, dtimes[-1] + oneDay])
    #ax1c.set_title("Measured transmit power (dBm)")

    ax1a.plot(validDbzDtimes, validDbzVals, \
              "o", label = 'DBZ diffs', color='blue')
    
    ax1a.plot(validDbzDtimes, validDbzVals, \
              label = 'DBZ diffs', linewidth=1, color='blue')
    
    ax1a.plot(validZdrDtimes, validZdrVals, \
              "o", label = 'ZDR diffs', color='red')
    
    ax1a.plot(validZdrDtimes, validZdrVals, \
              label = 'ZDR diffs', linewidth=1, color='red')
    
    ax1b.plot(dailyTimeDbz, dailyValDbz, \
              label = 'Daily DBZ Diffs', linewidth=1, color='blue')
    ax1b.plot(dailyTimeDbz, dailyValDbz, \
              "^", label = 'Daily DBZ Diffs', color='blue', markersize=10)

    ax1b.plot(dailyTimeZdr, dailyValZdr, \
              label = 'Daily ZDR Diffs', linewidth=1, color='red')
    ax1b.plot(dailyTimeZdr, dailyValZdr, \
              "^", label = 'Daily ZDR Diffs', color='red', markersize=10)

    #ax1c.plot(cptimes[validTxPwrH], TxPwrH[validTxPwrH], \
    #          label = 'TxPwrH', linewidth=2, color='blue')

    #ax1c.plot(cptimes[validTxPwrV], TxPwrV[validTxPwrV], \
    #          label = 'TxPwrV', linewidth=2, color='cyan')

    configDateAxis(ax1a, -4.0, 4.0, "Vol-by-vol diffs (dB)", 'upper right')
    configDateAxis(ax1b, -4.0, 4.0, "Daily mean diffs (dB)", 'upper right')
    #configDateAxis(ax1c, 85.0, 88.0, "Power (dBm)", 'upper right')

    fig1.autofmt_xdate()
    fig1.tight_layout()
    fig1.subplots_adjust(bottom=0.10, left=0.06, right=0.97, top=0.94)
    plt.show()

########################################################################
# initialize legends etc

def configDateAxis(ax, miny, maxy, ylabel, legendLoc):
    
    legend = ax.legend(loc=legendLoc, ncol=6)
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
# compute daily stats for a variable

def computeDailyStats(times, vals):

    dailyTimes = []
    dailyMeans = []

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
                sum = sum + val
                deltaTime = thisTime - thisDate
                sumDeltaTime = sumDeltaTime + deltaTime
                count = count + 1
                result.append(val)
        if (count > 5):
            mean = sum / count
            meanDeltaTime = datetime.timedelta(0, sumDeltaTime.total_seconds() / count)
            dailyMeans.append(mean)
            dailyTimes.append(thisDate + meanDeltaTime)
            # print >>sys.stderr, " daily time, meanStrong: ", dailyTimes[-1], meanStrong
            result.sort()
            
        thisDate = thisDate + oneDay

    return (dailyTimes, dailyMeans)


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

