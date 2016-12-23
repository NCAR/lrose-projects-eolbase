#!/usr/bin/env python

#===========================================================================
#
# Produce plots for self consistency analysis
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
    parser.add_option('--sc_file',
                      dest='scFilePath',
                      default='../data/pecan/self_consistency.txt',
                      help='Self consistency results file path')
    parser.add_option('--cp_file',
                      dest='cpFilePath',
                      default='../data/pecan/spol_pecan_CP_analysis_20150524_000021.txt',
                      help='CP results file path')
    parser.add_option('--title',
                      dest='title',
                      default='SELF CONSISTENCY FOR Z CHECK',
                      help='Title for plot')
    parser.add_option('--width',
                      dest='figWidthMm',
                      default=400,
                      help='Width of figure in mm')
    parser.add_option('--height',
                      dest='figHeightMm',
                      default=175,
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
        print >>sys.stderr, "  scFilePath: ", options.scFilePath
        print >>sys.stderr, "  cpFilePath: ", options.cpFilePath

    # read in column headers for self_con results

    iret, scHdrs, scData = readColumnHeaders(options.scFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for self_con results

    scData, scTimes = readInputData(options.scFilePath, scHdrs, scData)

    # read in column headers for CP results

    iret, cpHdrs, cpData = readColumnHeaders(options.cpFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for CP results

    cpData, cpTimes = readInputData(options.cpFilePath, cpHdrs, cpData)

    # render the plot
    
    doPlot(scData, scTimes, cpData, cpTimes)

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
                var == 'startGate' or var == 'endGate' or \
                var == 'npairsClut' or var == 'npairsWx' or \
                var == 'unix_time'):
                colData[var].append(int(data[index]))
            elif (var == 'fileName' or var == 'rayTime'):
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

def doPlot(scData, scTimes, cpData, cpTimes):

    widthIn = float(options.figWidthMm) / 25.4
    htIn = float(options.figHeightMm) / 25.4

    fig1 = plt.figure(1, (widthIn, htIn))
    ax1 = fig1.add_subplot(1,1,1,xmargin=0.0)
    ax1.plot(scTimes, np.zeros(len(scTimes)), linewidth=1, color = 'gray')
    
    fileName = options.scFilePath
    titleStr = "File: " + fileName
    hfmt = dates.DateFormatter('%y/%m/%d')

    lenMeanFilter = int(options.lenMean)
    
    # transmit power

    cptimes = np.array(cpTimes).astype(datetime.datetime)
    timeStart1us = datetime.datetime(2015, 6, 8, 0, 0, 0)
    pwrCorrFlag = cptimes < timeStart1us
    pwrCorr = np.zeros(len(cptimes))
    pwrCorr[cptimes < timeStart1us] = -1.76

    TxPwrH = np.array(cpData["TxPwrH"]).astype(np.double)
    TxPwrH = movingAverage(TxPwrH, lenMeanFilter)
    TxPwrH = TxPwrH + pwrCorr - 87.5
    validTxPwrH = np.isfinite(TxPwrH)

    TxPwrV = np.array(cpData["TxPwrV"]).astype(np.double)
    TxPwrV = movingAverage(TxPwrV, lenMeanFilter)
    TxPwrV = TxPwrV + pwrCorr - 87.5
    validTxPwrV = np.isfinite(TxPwrV)

    ax1.plot(cptimes[validTxPwrH], TxPwrH[validTxPwrH], \
             label = 'TxPwrH - 87.5', linewidth=1, color='blue')

    ax1.plot(cptimes[validTxPwrV], TxPwrV[validTxPwrV], \
             label = 'TxPwrV - 87.5', linewidth=1, color='cyan')

    # self-consistency dbz bias

    sctimes = np.array(scTimes).astype(datetime.datetime)

    
    elevDeg = np.array(scData["elevationDeg"]).astype(np.double)
    dbzBias = np.array(scData["dbzBias"]).astype(np.double)
    dbzBias = movingAverage(dbzBias, lenMeanFilter)
    validDbzBias = np.isfinite(dbzBias)

    #ax1.plot(sctimes[validDbzBias], dbzBias[validDbzBias], \
    #         label = 'DBZ bias', linewidth=1, color='red')

    ax1.plot(sctimes[validDbzBias], dbzBias[validDbzBias], \
             "o", linewidth=1, label = 'DBZ bias (dB)', color = 'orange')

    # daily mean dbz bias

    (dailyTimes, dailyMeans) = computeDailyMeans(scData, scTimes)

    ax1.plot(dailyTimes, dailyMeans, \
             linewidth=2, label = 'Daily mean bias (dB)', color = 'black')
    ax1.plot(dailyTimes, dailyMeans, \
             "k^", label = 'Daily mean bias (dB)', color = 'black', markersize=12)
    for ii, dailyBias in enumerate(dailyMeans):
        str = "{0:.2f}".format(dailyBias)
        ax1.annotate(str,
                     xy=(dailyTimes[ii], dailyBias),
                     xytext=(dailyTimes[ii] + datetime.timedelta(0.25),  dailyBias + 0.02),
                     # arrowprops=dict(facecolor='gray', shrink=0.01),
                     fontsize=18)
        

    # Scott's results

    scottTimes = [ datetime.datetime(2015, 05, 29, 12, 00, 00), \
                   datetime.datetime(2015, 06, 12, 12, 00, 00), \
                   datetime.datetime(2015, 06, 15, 12, 00, 00), \
                   datetime.datetime(2015, 06, 26, 12, 00, 00), \
                   datetime.datetime(2015, 07, 02, 12, 00, 00) ]

    scottBias = [ -1.39, -1.26, 2.78, 1.40, 0.75 ]

    ax1.plot(scottTimes, scottBias, \
             linewidth=2, label = 'Scott bias (dB)', color = 'red')
    ax1.plot(scottTimes, scottBias, \
             "^", label = 'Scott bias (dB)', color = 'red', markersize=12)

    # mean bias for early and late parts of project
    
    startTime = datetime.datetime(2015, 05, 28, 0, 0, 0)
    endTime = datetime.datetime(2015, 06, 05, 0, 0, 0)
    meanBiasEarly = computeMeanBias(scData, scTimes, startTime, endTime)
    print >>sys.stderr, "Mean bias early, May 28 - June 5: ", meanBiasEarly

    startTime = datetime.datetime(2015, 06, 14, 0, 0, 0)
    endTime = datetime.datetime(2015, 07, 17, 0, 0, 0)
    meanBiasLate = computeMeanBias(scData, scTimes, startTime, endTime)
    print >>sys.stderr, "Mean bias late, June 14 - July 17: ", meanBiasLate

    meanTimes =  [ datetime.datetime(2015, 05, 28, 00, 00, 00), \
                   datetime.datetime(2015, 06, 05, 00, 00, 00), \
                   datetime.datetime(2015, 06, 14, 00, 00, 00), \
                   datetime.datetime(2015, 07, 17, 00, 00, 00) ]

    meanBias = [ meanBiasEarly, meanBiasEarly, meanBiasLate, meanBiasLate]

    ax1.plot(meanTimes, meanBias, \
             linewidth=2, label = 'Mean bias = (dB)', color = 'green')
    ax1.plot(meanTimes, meanBias, \
             "^", label = 'Mean bias (dB)', color = 'green', markersize=12)

    # legends, azes etc

    legend1 = ax1.legend(loc='upper right', ncol=7)
    for label in legend1.get_texts():
        label.set_fontsize('x-small')
    ax1.set_xlabel("Date")
    ax1.set_ylabel("DBZ BIAS / Xmit Pwr (dB)")
    ax1.grid(True)
    ax1.set_ylim([-5, 5])
    
    hfmt = dates.DateFormatter('%y/%m/%d')
    ax1.xaxis.set_major_locator(dates.DayLocator())
    ax1.xaxis.set_major_formatter(hfmt)
    
    for tick in ax1.xaxis.get_major_ticks():
        tick.label.set_fontsize(8) 

    fig1.suptitle("Original self-consistency analysis - SPOL - PECAN")
    fig1.autofmt_xdate()
    plt.tight_layout()
    plt.subplots_adjust(top=0.96)
    plt.show()

########################################################################
# compute daily means for dbz bias

def computeDailyMeans(scData, scTimes):

    dailyTimes = []
    dailyMeans = []

    sctimes = np.array(scTimes).astype(datetime.datetime)
    dbzBias = np.array(scData["dbzBias"]).astype(np.double)

    validDbzBias = np.isfinite(dbzBias)
    goodBiases = dbzBias[validDbzBias]
    goodTimes = sctimes[validDbzBias]

    startTime = sctimes[0]
    endTime = sctimes[-1]

    startDate = datetime.datetime(startTime.year, startTime.month, startTime.day, 0, 0, 0)
    endDate = datetime.datetime(endTime.year, endTime.month, endTime.day, 0, 0, 0)

    oneDay = datetime.timedelta(1)
    halfDay = datetime.timedelta(0.5)

    thisDate = startDate
    while (thisDate < endDate + oneDay):

        nextDate = thisDate + oneDay
        
        sumBias = 0.0
        sumDeltaTime = datetime.timedelta(0)
        count = 0.0
        for ii, bias in enumerate(goodBiases, start=0):
            thisTime = goodTimes[ii]
            if (thisTime >= thisDate and thisTime < nextDate):
                sumBias = sumBias + bias
                deltaTime = thisTime - thisDate
                sumDeltaTime = sumDeltaTime + deltaTime
                count = count + 1
        if (count > 10):
            meanBias = sumBias / count
            meanDeltaTime = datetime.timedelta(0, sumDeltaTime.total_seconds() / count)
            dailyMeans.append(meanBias)
            dailyTimes.append(thisDate + meanDeltaTime)
            # print >>sys.stderr, " daily time, meanBias: ", dailyTimes[-1], meanBias
            
        thisDate = thisDate + oneDay

    return (dailyTimes, dailyMeans)


########################################################################
# compute daily means for dbz bias

def computeMeanBias(scData, scTimes, startTime, endTime):

    sctimes = np.array(scTimes).astype(datetime.datetime)
    dbzBias = np.array(scData["dbzBias"]).astype(np.double)
    
    validDbzBias = np.isfinite(dbzBias)
    goodBiases = dbzBias[validDbzBias]
    goodTimes = sctimes[validDbzBias]
    
    sumBias = 0.0
    count = 0.0
    for ii, bias in enumerate(goodBiases, start=0):
        thisTime = goodTimes[ii]
        if (thisTime >= startTime and thisTime < endTime):
            sumBias = sumBias + bias
            count = count + 1
            # print >>sys.stderr, " time, bias: ", thisTime, bias

    if (count > 1):
        meanBias = sumBias / count

    return meanBias
            
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

