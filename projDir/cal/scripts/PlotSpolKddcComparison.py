#!/usr/bin/env python

#===========================================================================
#
# Produce plots for dbz comparison between spol and kddc
#
#===========================================================================

import os
import sys
import subprocess
from optparse import OptionParser
import numpy as np
import numpy.ma as ma
from numpy import convolve
import matplotlib.pyplot as plt
from matplotlib import dates
import math
import datetime
import contextlib

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
    parser.add_option('--comp_file',
                      dest='compFilePath',
                      default='../data/pecan/spol_kddc_comparison.txt',
                      help='RadxSunMon results file path')
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
                      default='COMPARISON BETWEEN SPOL AND KDDC - PECAN',
                      help='Title for plot')
    parser.add_option('--width',
                      dest='figWidthMm',
                      default=400,
                      help='Width of figure in mm')
    parser.add_option('--height',
                      dest='figHeightMm',
                      default=320,
                      help='Height of figure in mm')
    parser.add_option('--meanLen',
                      dest='meanLen',
                      default=1,
                      help='Len of moving mean filter')
    parser.add_option('--kddcAdjustDb',
                      dest='kddcAdjustDb',
                      default=0,
                      help='Adjustment to Dodge City DBZ (dB)')
    
    (options, args) = parser.parse_args()
    
    if (options.verbose == True):
        options.debug = True

    if (options.debug == True):
        print >>sys.stderr, "Running %prog"
        print >>sys.stderr, "  compFilePath: ", options.compFilePath
        print >>sys.stderr, "  scFilePath: ", options.scFilePath

    # read in column headers for comparison results

    iret, compHdrs, compData = readColumnHeaders(options.compFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for comparison results

    compTimes, compData = readInputData(options.compFilePath, compHdrs, compData)

    # read in column headers for self_con results

    iret, scHdrs, scData = readColumnHeaders(options.scFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for self_con results
    
    scTimes, scData = readInputData(options.scFilePath, scHdrs, scData)

    # read in column headers for CP results

    iret, cpHdrs, cpData = readColumnHeaders(options.cpFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for CP results

    cpTimes, cpData = readInputData(options.cpFilePath, cpHdrs, cpData)

    # render the plot
    
    doPlot(compTimes, compData, scTimes, scData, cpTimes, cpData)

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
    fp.close()

    # read in a line at a time, set colData
    for line in lines:
        
        commentIndex = line.find("#")
        if (commentIndex >= 0):
            continue
            
        # data
        
        data = line.strip().split()

        for index, var in enumerate(colHeaders, start=0):
            if (var == 'count' or \
                var == 'year' or var == 'month' or var == 'day' or \
                var == 'hour' or var == 'min' or var == 'sec' or \
                var == 'nBeamsNoise'):
                colData[var].append(int(data[index]))
            else:
                if (isNumber(data[index])):
                    colData[var].append(float(data[index]))
                else:
                    colData[var].append(data[index])

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

    return obsTimes, colData

########################################################################
# Check is a number

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

########################################################################
# Moving average filter

def movingAverage(values, filtLen):

    weights = np.repeat(1.0, filtLen)/filtLen
    sma = np.convolve(values, weights, 'valid')
    smaList = sma.tolist()
    for ii in range(0, filtLen / 2):
        smaList.insert(0, smaList[0])
        smaList.append(smaList[-1])
    return np.array(smaList).astype(np.double)

########################################################################
# Plot

def doPlot(compTimes, compData, scTimes, scData, cpTimes, cpData):

    fileName = options.compFilePath
    titleStr = "File: " + fileName
    hfmt = dates.DateFormatter('%y/%m/%d')

    # comparison times
    
    comptimes = np.array(compTimes).astype(datetime.datetime)
    
    # load up stats
    
    nPts = np.array(compData["nPts"]).astype(np.double)
    meanDiff = np.array(compData["meanDiff"]).astype(np.double) - float(options.kddcAdjustDb)
    validMeanDiff = np.isfinite(meanDiff)
    smoothedMeanDiff = movingAverage(meanDiff[validMeanDiff], int(options.meanLen))

    medianDiff = np.array(compData["medianDiff"]).astype(np.double) - float(options.kddcAdjustDb)
    validMedianDiff = np.isfinite(medianDiff)
    smoothedMedianDiff = movingAverage(medianDiff[validMedianDiff], int(options.meanLen))

    sdevDiff = np.array(compData["sdevDiff"]).astype(np.double)
    validSdevDiff = np.isfinite(sdevDiff)
    smoothedSdevDiff = movingAverage(sdevDiff[validSdevDiff], int(options.meanLen))

    # daily mean dbz diff

    (meanDiffDailyTimes, meanDiffDaily) = computeWeightedStats(comptimes[validMeanDiff], \
                                                               meanDiff[validMeanDiff], \
                                                               nPts[validMeanDiff])

    # self-consistency dbz bias

    sctimes = np.array(scTimes).astype(datetime.datetime)
    dbzBias = np.array(scData["dbzBias"]).astype(np.double)
    dbzBias = movingAverage(dbzBias, int(options.meanLen))
    validDbzBias = np.isfinite(dbzBias)

    # daily mean dbz bias

    (dbzBiasDailyTimes, dbzBiasDailyMeans) = computeDailyStats(scTimes, scData["dbzBias"])

    # transmit power - axis 3

    cptimes = np.array(cpTimes).astype(datetime.datetime)
    timeStart1us = datetime.datetime(2015, 6, 8, 0, 0, 0)
    pwrCorrFlag = cptimes < timeStart1us
    pwrCorr = np.zeros(len(cptimes))
    pwrCorr[cptimes < timeStart1us] = -1.76

    TxPwrH = np.array(cpData["TxPwrH"]).astype(np.double)
    TxPwrH = movingAverage(TxPwrH, int(options.meanLen))
    TxPwrH = TxPwrH + pwrCorr
    validTxPwrH = np.isfinite(TxPwrH)

    TxPwrV = np.array(cpData["TxPwrV"]).astype(np.double)
    TxPwrV = movingAverage(TxPwrV, int(options.meanLen))
    TxPwrV = TxPwrV + pwrCorr
    validTxPwrV = np.isfinite(TxPwrV)

    # set up plot structure

    widthIn = float(options.figWidthMm) / 25.4
    htIn = float(options.figHeightMm) / 25.4

    fig1 = plt.figure(1, (widthIn, htIn))
    ax1 = fig1.add_subplot(3,1,1,xmargin=0.0)
    ax2 = fig1.add_subplot(3,1,2,xmargin=0.0)
    ax3 = fig1.add_subplot(3,1,3,xmargin=0.0)

    oneDay = datetime.timedelta(1.0)
    ax1.set_xlim([comptimes[0] - oneDay, comptimes[-1] + oneDay])
    ax2.set_xlim([comptimes[0] - oneDay, comptimes[-1] + oneDay])
    ax3.set_xlim([comptimes[0] - oneDay, comptimes[-1] + oneDay])

    # plot comparison results - axis 1

    ax1.plot(comptimes, smoothedMeanDiff, \
             label = 'mean diff', linewidth=1, color='blue')
    #ax1.plot(comptimes, smoothedMedianDiff, \
    #         label = 'median diff', linewidth=1, color='red')
    #ax1.plot(comptimes, smoothedSdevDiff, \
    #         label = 'sdev diff', linewidth=1, color='green')

    ax1.plot(meanDiffDailyTimes, meanDiffDaily, \
             linewidth=2, color = 'red', markersize=12)
    ax1.plot(meanDiffDailyTimes, meanDiffDaily, \
             "^", label = 'Daily mean diff (dB)', color = 'red', markersize=12)
    for ii, meanDiff in enumerate(meanDiffDaily):
        strf = "{0:.2f}".format(meanDiff)
        ax1.annotate(strf,
                     xy=(meanDiffDailyTimes[ii], meanDiff),
                     xytext=(meanDiffDailyTimes[ii] + datetime.timedelta(0.25),  meanDiff + 0.02),
                     fontsize=18, color='red')

    # plot self consistency results - axis 2
    
    ax2.plot(sctimes[validDbzBias], dbzBias[validDbzBias], \
             "o", linewidth=1, label = 'DBZ bias (dB)', color = 'orange')

    ax2.plot(dbzBiasDailyTimes, dbzBiasDailyMeans, \
             linewidth=2, label = 'Daily mean bias (dB)', color = 'black')
    ax2.plot(dbzBiasDailyTimes, dbzBiasDailyMeans, \
             "^", label = 'Daily mean bias (dB)', color = 'black', markersize=12)
    for ii, dailyBias in enumerate(dbzBiasDailyMeans):
        strf = "{0:.2f}".format(dailyBias)
        ax2.annotate(strf,
                     xy=(dbzBiasDailyTimes[ii], dailyBias),
                     xytext=(dbzBiasDailyTimes[ii] + datetime.timedelta(0.25),  dailyBias + 0.02),
                     fontsize=18)

    # transmit power - axis 3

    ax3.plot(cptimes[validTxPwrH], TxPwrH[validTxPwrH], \
             label = 'TxPwrH', linewidth=1, color='blue')

    ax3.plot(cptimes[validTxPwrV], TxPwrV[validTxPwrV], \
             label = 'TxPwrV', linewidth=1, color='cyan')

    xmitPwrDailyTimesH, xmitPwrHDailyMeans = computeDailyStats(cpTimes, TxPwrH)
    ax3.plot(xmitPwrDailyTimesH, xmitPwrHDailyMeans, \
             linewidth=2, label = 'Daily mean H pwr (dBm)', color = 'red')
    ax3.plot(xmitPwrDailyTimesH, xmitPwrHDailyMeans, \
             "^", label = 'Daily mean bias (dB)', color = 'red', markersize=6)

    for ii, pwr in enumerate(xmitPwrHDailyMeans):
        if (ii % 4 == 0):
            strf = "{0:.2f}".format(pwr)
            ax3.annotate(strf,
                         xy=(xmitPwrDailyTimesH[ii], pwr),
                         xytext=(xmitPwrDailyTimesH[ii] + \
                                 datetime.timedelta(0.25), pwr + 0.02),
                         color='red',
                         fontsize=15)

    xmitPwrDailyTimesV, xmitPwrVDailyMeans = computeDailyStats(cpTimes, TxPwrV)
    ax3.plot(xmitPwrDailyTimesV, xmitPwrVDailyMeans, \
             linewidth=2, label = 'Daily mean V pwr (dBm)', color = 'green')
    ax3.plot(xmitPwrDailyTimesV, xmitPwrVDailyMeans, \
             "^", label = 'Daily mean bias (dB)', color = 'green', markersize=6)

    for ii, pwr in enumerate(xmitPwrVDailyMeans):
        if (ii % 4 == 0):
            strf = "{0:.2f}".format(pwr)
            ax3.annotate(strf,
                         xy=(xmitPwrDailyTimesV[ii], pwr),
                         xytext=(xmitPwrDailyTimesV[ii] + \
                                 datetime.timedelta(0.25), pwr + 0.02),
                         color='green',
                         fontsize=15)

    # legends etc
    
    configureAxis(ax1, -4, 4, "SPOL - KDDC (dB)", 'upper left')
    configureAxis(ax2, -9999.0, -9999.0, "SELF CONSISTENCY BIAS (dB)", 'upper left')
    #configureAxis(ax3, 87, 88, "Xmit Power (dBM)", 'upper left')
    configureAxis(ax3, 84, 90, "Xmit Power (dBM)", 'upper left')

    adjustDb = str(options.kddcAdjustDb)
    fig1.suptitle("RADAR COMPARISON SPOL-KDDC, KDDC adjusted by " + \
                  adjustDb + " dB" + \
                  " and SELF-CONSISTENCY CHECK ON SPOL")
    fig1.autofmt_xdate()

    plt.tight_layout()
    plt.subplots_adjust(top=0.96)
    plt.show()

########################################################################
# initialize legends etc

def configureAxis(ax, miny, maxy, ylabel, legendLoc):
    
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
# get flux closest in time to the search time

def getClosestFlux(hcTime, fluxTimes, obsFlux):

    minDeltaTime = 1.0e99
    fltime = fluxTimes[0]
    flux = obsFlux[0]
    for ii, ftime in enumerate(fluxTimes, start=0):
        deltaTime = math.fabs((ftime - hcTime).total_seconds())
        if (deltaTime < minDeltaTime):
            minDeltaTime = deltaTime
            flux = obsFlux[ii]
            #if (flux > 150.0):
            #    flux = 150.0
            fltime = ftime
            
    return (fltime, flux)

########################################################################
# compute daily means for dbz bias

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
        if (count > 1):
            mean = sum / count
            meanDeltaTime = datetime.timedelta(0, sumDeltaTime.total_seconds() / count)
            dailyMeans.append(mean)
            dailyTimes.append(thisDate + meanDeltaTime)
            # print >>sys.stderr, " daily time, meanStrong: ", dailyTimes[-1], meanStrong
            result.sort()
            
        thisDate = thisDate + oneDay

    return (dailyTimes, dailyMeans)


########################################################################
# compute weighted daily means for dbz bias

def computeWeightedStats(times, vals, npts):

    dailyTimes = []
    dailyMeans = []

    nptimes = np.array(times).astype(datetime.datetime)
    npvals = np.array(vals).astype(np.double)
    npnpts = np.array(npts).astype(np.double)

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
            thisNpts = npnpts[ii]
            if (thisTime >= thisDate and thisTime < nextDate):
                sum = sum + val * thisNpts
                deltaTime = thisTime - thisDate
                sumDeltaTime = sumDeltaTime + deltaTime
                count = count + thisNpts
                result.append(val)
        if (count > 50000):
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

